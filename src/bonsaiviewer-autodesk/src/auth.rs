use std::io::{BufRead, BufReader, Write};
use std::net::TcpListener;
use std::sync::Arc;
use std::time::Duration;

use base64::engine::general_purpose::URL_SAFE_NO_PAD;
use base64::Engine;
use chrono::{DateTime, Duration as ChronoDuration, Utc};
use rand::rngs::OsRng;
use rand::RngCore;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};

use crate::progress::AuthProgress;
use crate::rpc::RpcError;

pub const KEYRING_SERVICE: &str = "bonsaiviewer-autodesk";
pub const AUTHORIZE_ENDPOINT: &str =
    "https://developer.api.autodesk.com/authentication/v2/authorize";
pub const TOKEN_ENDPOINT: &str = "https://developer.api.autodesk.com/authentication/v2/token";

const REFRESH_TTL_DEFAULT_SECONDS: i64 = 15 * 24 * 60 * 60;
const TOKEN_SKEW_SECONDS: i64 = 30;

fn no_keyring_error() -> RpcError {
    RpcError::internal(
        "No secure keyring backend is available. On macOS, use Keychain; \
         on Windows, use Credential Manager; on Linux, install a Secret \
         Service backend such as gnome-keyring or KWallet.",
    )
}

/// Abstract token storage so tests can swap in an in-memory backend.
pub trait TokenStore: Send + Sync {
    fn load(&self) -> Result<Option<StoredToken>, RpcError>;
    fn save(&self, token: &StoredToken) -> Result<(), RpcError>;
    fn delete(&self) -> Result<(), RpcError>;
}

pub struct KeyringTokenStore {
    pub service: String,
    pub username: String,
}

impl KeyringTokenStore {
    pub fn new(username: impl Into<String>) -> Self {
        Self {
            service: KEYRING_SERVICE.to_string(),
            username: username.into(),
        }
    }

    fn entry(&self) -> Result<keyring::Entry, RpcError> {
        keyring::Entry::new(&self.service, &self.username).map_err(|_| no_keyring_error())
    }
}

impl TokenStore for KeyringTokenStore {
    fn load(&self) -> Result<Option<StoredToken>, RpcError> {
        match self.entry()?.get_password() {
            Ok(raw) => serde_json::from_str(&raw)
                .map(Some)
                .map_err(|e| RpcError::internal(format!("Stored token is corrupt: {e}"))),
            Err(keyring::Error::NoEntry) => Ok(None),
            Err(keyring::Error::PlatformFailure(_)) | Err(keyring::Error::NoStorageAccess(_)) => {
                Err(no_keyring_error())
            }
            Err(e) => Err(RpcError::internal(format!("Keyring read failed: {e}"))),
        }
    }

    fn save(&self, token: &StoredToken) -> Result<(), RpcError> {
        let serialised = serde_json::to_string(token)
            .map_err(|e| RpcError::internal(format!("Serialise token failed: {e}")))?;
        self.entry()?
            .set_password(&serialised)
            .map_err(|_| no_keyring_error())
    }

    fn delete(&self) -> Result<(), RpcError> {
        match self.entry()?.delete_credential() {
            Ok(()) | Err(keyring::Error::NoEntry) => Ok(()),
            Err(keyring::Error::PlatformFailure(_)) | Err(keyring::Error::NoStorageAccess(_)) => {
                Err(no_keyring_error())
            }
            Err(e) => Err(RpcError::internal(format!("Keyring delete failed: {e}"))),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize, PartialEq, Eq)]
pub struct StoredToken {
    pub client_id: String,
    pub access_token: String,
    pub refresh_token: String,
    pub access_token_expires_at: DateTime<Utc>,
    pub refresh_token_expires_at: DateTime<Utc>,
    pub scope: String,
}

fn base64url(bytes: &[u8]) -> String {
    URL_SAFE_NO_PAD.encode(bytes)
}

pub fn generate_code_verifier() -> String {
    let mut buf = [0u8; 48];
    OsRng.fill_bytes(&mut buf);
    base64url(&buf)
}

pub fn generate_code_challenge(verifier: &str) -> String {
    let digest = Sha256::digest(verifier.as_bytes());
    base64url(&digest)
}

pub fn generate_state() -> String {
    let mut buf = [0u8; 16];
    OsRng.fill_bytes(&mut buf);
    let mut s = String::with_capacity(32);
    for b in &buf {
        s.push_str(&format!("{b:02x}"));
    }
    s
}

/// Block on a single OAuth redirect to `http://host:port/path` and return the
/// authorization code. Handles exactly one request, then closes.
pub fn wait_for_oauth_callback(
    host: &str,
    port: u16,
    path: &str,
    expected_state: &str,
) -> Result<String, RpcError> {
    let listener = TcpListener::bind((host, port)).map_err(|e| {
        RpcError::internal(format!("Cannot bind OAuth callback to {host}:{port}: {e}"))
    })?;
    let (mut stream, _) = listener
        .accept()
        .map_err(|e| RpcError::internal(format!("OAuth callback accept failed: {e}")))?;
    stream.set_read_timeout(Some(Duration::from_secs(30))).ok();

    let request_line = {
        let mut reader = BufReader::new(
            stream
                .try_clone()
                .map_err(|e| RpcError::internal(e.to_string()))?,
        );
        let mut line = String::new();
        reader
            .read_line(&mut line)
            .map_err(|e| RpcError::internal(e.to_string()))?;
        line
    };

    let target = request_line.split_whitespace().nth(1).unwrap_or("/");
    let (req_path, query) = match target.split_once('?') {
        Some((p, q)) => (p, q),
        None => (target, ""),
    };

    let matched = req_path == path;
    let body: &[u8] = if matched {
        b"<html><body><h2>Authentication complete. You can close this window.</h2></body></html>"
    } else {
        b"<html><body><h2>Not Found</h2></body></html>"
    };
    let status = if matched { "200 OK" } else { "404 Not Found" };
    let header = format!(
        "HTTP/1.1 {status}\r\nContent-Type: text/html; charset=utf-8\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
        body.len()
    );
    let _ = stream.write_all(header.as_bytes());
    let _ = stream.write_all(body);
    let _ = stream.flush();

    if !matched {
        return Err(RpcError::internal("OAuth callback hit unexpected path."));
    }

    let mut state: Option<String> = None;
    let mut code: Option<String> = None;
    let mut error: Option<String> = None;
    for (k, v) in url::form_urlencoded::parse(query.as_bytes()) {
        match k.as_ref() {
            "state" => state = Some(v.into_owned()),
            "code" => code = Some(v.into_owned()),
            "error" => error = Some(v.into_owned()),
            _ => {}
        }
    }

    if let Some(err) = error.filter(|s| !s.is_empty()) {
        return Err(RpcError::internal(format!(
            "Autodesk returned OAuth error '{err}'."
        )));
    }
    if state.as_deref() != Some(expected_state) {
        return Err(RpcError::internal("OAuth state mismatch."));
    }
    code.filter(|s| !s.is_empty())
        .ok_or_else(|| RpcError::internal("OAuth callback did not return an authorization code."))
}

/// Pluggable callback strategy — production binds a localhost socket, tests
/// inject a stub that returns a canned code.
pub type CallbackWaiter =
    Arc<dyn Fn(&str, u16, &str, &str) -> Result<String, RpcError> + Send + Sync>;

pub fn default_callback_waiter() -> CallbackWaiter {
    Arc::new(wait_for_oauth_callback)
}

/// Pluggable "open this URL in a browser" — production opens it for real,
/// tests use a no-op.
pub type Browser = Arc<dyn Fn(&str) + Send + Sync>;

pub fn default_browser() -> Browser {
    Arc::new(|url| {
        let _ = webbrowser::open(url);
    })
}

pub struct AuthSessionService {
    pub client_id: String,
    pub callback_url: String,
    pub scope: String,
    token_store: Box<dyn TokenStore>,
    callback_waiter: CallbackWaiter,
    browser: Browser,
    authorize_endpoint: String,
    token_endpoint: String,
    agent: ureq::Agent,
}

pub struct AuthBuilder {
    client_id: String,
    callback_url: String,
    scope: String,
    token_store: Box<dyn TokenStore>,
    callback_waiter: CallbackWaiter,
    browser: Browser,
    authorize_endpoint: String,
    token_endpoint: String,
}

impl AuthBuilder {
    pub fn new(
        client_id: String,
        callback_url: String,
        scope: String,
        token_store: Box<dyn TokenStore>,
    ) -> Self {
        Self {
            client_id,
            callback_url,
            scope,
            token_store,
            callback_waiter: default_callback_waiter(),
            browser: default_browser(),
            authorize_endpoint: AUTHORIZE_ENDPOINT.to_string(),
            token_endpoint: TOKEN_ENDPOINT.to_string(),
        }
    }

    pub fn with_callback_waiter(mut self, waiter: CallbackWaiter) -> Self {
        self.callback_waiter = waiter;
        self
    }
    pub fn with_browser(mut self, browser: Browser) -> Self {
        self.browser = browser;
        self
    }
    pub fn with_endpoints(mut self, authorize: String, token: String) -> Self {
        self.authorize_endpoint = authorize;
        self.token_endpoint = token;
        self
    }

    pub fn build(self) -> AuthSessionService {
        AuthSessionService {
            client_id: self.client_id,
            callback_url: self.callback_url,
            scope: self.scope,
            token_store: self.token_store,
            callback_waiter: self.callback_waiter,
            browser: self.browser,
            authorize_endpoint: self.authorize_endpoint,
            token_endpoint: self.token_endpoint,
            agent: ureq::AgentBuilder::new()
                .timeout(Duration::from_secs(60))
                .build(),
        }
    }
}

impl AuthSessionService {
    pub fn new(client_id: String, callback_url: String, scope: String) -> Self {
        let store = Box::new(KeyringTokenStore::new(client_id.clone()));
        AuthBuilder::new(client_id, callback_url, scope, store).build()
    }

    pub fn get_token(&self) -> Result<Option<StoredToken>, RpcError> {
        self.token_store.load()
    }

    pub fn sign_out(&self) -> Result<(), RpcError> {
        self.token_store.delete()
    }

    pub fn ensure_access_token(&self, progress: AuthProgress) -> Result<String, RpcError> {
        let token = self.token_store.load()?;
        let now = Utc::now();
        if let Some(t) = &token {
            if t.access_token_expires_at > now + ChronoDuration::minutes(1) {
                return Ok(t.access_token.clone());
            }
            if t.refresh_token_expires_at > now + ChronoDuration::minutes(1) {
                return Ok(self.refresh(t, progress)?.access_token);
            }
        }
        Ok(self.login_interactive(progress)?.access_token)
    }

    pub fn login_interactive(&self, progress: AuthProgress) -> Result<StoredToken, RpcError> {
        progress("auth", "Preparing Autodesk sign-in", None);
        let verifier = generate_code_verifier();
        let challenge = generate_code_challenge(&verifier);
        let state = generate_state();
        let callback = url::Url::parse(&self.callback_url)
            .map_err(|e| RpcError::internal(format!("Bad callback URL: {e}")))?;
        if callback.scheme() != "http"
            || !matches!(callback.host_str(), Some("127.0.0.1") | Some("localhost"))
        {
            return Err(RpcError::internal(
                "Callback URL must be http://localhost or http://127.0.0.1.",
            ));
        }

        let authorize_url = {
            let mut u = url::Url::parse(&self.authorize_endpoint)
                .map_err(|e| RpcError::internal(format!("Bad authorize endpoint: {e}")))?;
            u.query_pairs_mut()
                .append_pair("response_type", "code")
                .append_pair("client_id", &self.client_id)
                .append_pair("redirect_uri", &self.callback_url)
                .append_pair("scope", &self.scope)
                .append_pair("code_challenge", &challenge)
                .append_pair("code_challenge_method", "S256")
                .append_pair("state", &state);
            u.to_string()
        };

        progress("auth", "Opening browser for Autodesk sign-in", None);
        (self.browser)(&authorize_url);

        let host = callback.host_str().unwrap_or("127.0.0.1");
        let port = callback.port().unwrap_or(80);
        let path = callback.path();
        let code = (self.callback_waiter)(host, port, path, &state)?;

        progress("auth", "Exchanging authorization code for token", None);
        let payload = self.post_form(&[
            ("client_id", self.client_id.as_str()),
            ("grant_type", "authorization_code"),
            ("code", code.as_str()),
            ("code_verifier", verifier.as_str()),
            ("redirect_uri", self.callback_url.as_str()),
        ])?;
        let token = self.token_from_payload(&payload)?;
        self.token_store.save(&token)?;
        progress("auth", "Signed in to Autodesk", Some(100));
        Ok(token)
    }

    fn refresh(
        &self,
        token: &StoredToken,
        progress: AuthProgress,
    ) -> Result<StoredToken, RpcError> {
        progress("auth", "Refreshing Autodesk session", None);
        let payload = self
            .post_form(&[
                ("client_id", self.client_id.as_str()),
                ("grant_type", "refresh_token"),
                ("refresh_token", token.refresh_token.as_str()),
                ("scope", self.scope.as_str()),
            ])
            .map_err(|e| RpcError::internal(format!("Token refresh failed: {}", e.message)))?;
        let refreshed = self.token_from_payload(&payload)?;
        self.token_store.save(&refreshed)?;
        progress("auth", "Session refreshed", Some(100));
        Ok(refreshed)
    }

    fn post_form(&self, form: &[(&str, &str)]) -> Result<Value, RpcError> {
        match self.agent.post(&self.token_endpoint).send_form(form) {
            Ok(resp) => resp
                .into_json::<Value>()
                .map_err(|e| RpcError::internal(format!("Token endpoint returned non-JSON: {e}"))),
            Err(ureq::Error::Status(_, resp)) => {
                let body = resp.into_string().unwrap_or_default();
                Err(RpcError::internal(format!("Token exchange failed: {body}")))
            }
            Err(e) => Err(RpcError::internal(format!("Token request failed: {e}"))),
        }
    }

    fn token_from_payload(&self, payload: &Value) -> Result<StoredToken, RpcError> {
        let now = Utc::now();
        let expires_in = payload
            .get("expires_in")
            .and_then(|v| v.as_i64())
            .ok_or_else(|| RpcError::internal("Token response missing 'expires_in'."))?;
        let refresh_ttl = payload
            .get("refresh_token_expires_in")
            .and_then(|v| v.as_i64())
            .unwrap_or(REFRESH_TTL_DEFAULT_SECONDS);
        let access_token = payload
            .get("access_token")
            .and_then(|v| v.as_str())
            .ok_or_else(|| RpcError::internal("Token response missing 'access_token'."))?;
        let refresh_token = payload
            .get("refresh_token")
            .and_then(|v| v.as_str())
            .ok_or_else(|| RpcError::internal("Token response missing 'refresh_token'."))?;
        Ok(StoredToken {
            client_id: self.client_id.clone(),
            access_token: access_token.to_string(),
            refresh_token: refresh_token.to_string(),
            access_token_expires_at: now + ChronoDuration::seconds(expires_in - TOKEN_SKEW_SECONDS),
            refresh_token_expires_at: now
                + ChronoDuration::seconds(refresh_ttl - TOKEN_SKEW_SECONDS),
            scope: self.scope.clone(),
        })
    }
}

/// In-memory token store for tests and ephemeral sessions.
pub struct InMemoryTokenStore {
    inner: std::sync::Mutex<Option<StoredToken>>,
}

impl InMemoryTokenStore {
    pub fn empty() -> Self {
        Self {
            inner: std::sync::Mutex::new(None),
        }
    }
    pub fn preloaded(token: StoredToken) -> Self {
        Self {
            inner: std::sync::Mutex::new(Some(token)),
        }
    }
}

impl TokenStore for InMemoryTokenStore {
    fn load(&self) -> Result<Option<StoredToken>, RpcError> {
        Ok(self.inner.lock().unwrap().clone())
    }
    fn save(&self, token: &StoredToken) -> Result<(), RpcError> {
        *self.inner.lock().unwrap() = Some(token.clone());
        Ok(())
    }
    fn delete(&self) -> Result<(), RpcError> {
        *self.inner.lock().unwrap() = None;
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::sync::Mutex;

    #[test]
    fn code_challenge_matches_known_pkce_vector() {
        // RFC 7636 appendix B
        let verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk";
        assert_eq!(
            generate_code_challenge(verifier),
            "E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM"
        );
    }

    #[test]
    fn verifier_and_state_length() {
        let v = generate_code_verifier();
        assert!(v.len() >= 43);
        let s = generate_state();
        assert_eq!(s.len(), 32);
    }

    #[test]
    fn store_round_trip_in_memory() {
        let token = StoredToken {
            client_id: "x".into(),
            access_token: "a".into(),
            refresh_token: "r".into(),
            access_token_expires_at: Utc::now(),
            refresh_token_expires_at: Utc::now(),
            scope: "s".into(),
        };
        let store = InMemoryTokenStore::empty();
        assert!(store.load().unwrap().is_none());
        store.save(&token).unwrap();
        assert_eq!(store.load().unwrap().as_ref(), Some(&token));
        store.delete().unwrap();
        assert!(store.load().unwrap().is_none());
    }

    fn make_service(
        store: Box<dyn TokenStore>,
        token_endpoint: String,
        code: &'static str,
    ) -> AuthSessionService {
        AuthBuilder::new(
            "client-xyz".into(),
            "http://127.0.0.1:8080/".into(),
            "data:read".into(),
            store,
        )
        .with_callback_waiter(Arc::new(move |_, _, _, _| Ok(code.to_string())))
        .with_browser(Arc::new(|_| {}))
        .with_endpoints("https://example.invalid/authorize".into(), token_endpoint)
        .build()
    }

    /// Tiny single-shot HTTP responder for the token endpoint.
    fn spawn_token_endpoint(response_body: &'static str) -> String {
        use std::thread;
        let listener = TcpListener::bind("127.0.0.1:0").unwrap();
        let port = listener.local_addr().unwrap().port();
        thread::spawn(move || {
            let (mut stream, _) = listener.accept().unwrap();
            // Drain request headers (best-effort)
            let mut reader = BufReader::new(stream.try_clone().unwrap());
            let mut line = String::new();
            loop {
                line.clear();
                if reader.read_line(&mut line).unwrap_or(0) == 0 {
                    break;
                }
                if line == "\r\n" || line == "\n" {
                    break;
                }
            }
            let body = response_body.as_bytes();
            let response = format!(
                "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {}\r\nConnection: close\r\n\r\n",
                body.len()
            );
            let _ = stream.write_all(response.as_bytes());
            let _ = stream.write_all(body);
            let _ = stream.flush();
        });
        format!("http://127.0.0.1:{port}/")
    }

    #[test]
    fn login_interactive_saves_token() {
        let endpoint = spawn_token_endpoint(
            r#"{"access_token":"AT","refresh_token":"RT","expires_in":3600,"refresh_token_expires_in":86400}"#,
        );
        let store = Box::new(InMemoryTokenStore::empty());
        let saved_check: Arc<Mutex<Option<StoredToken>>> = Arc::new(Mutex::new(None));
        struct PeekStore {
            shadow: Arc<Mutex<Option<StoredToken>>>,
            inner: InMemoryTokenStore,
        }
        impl TokenStore for PeekStore {
            fn load(&self) -> Result<Option<StoredToken>, RpcError> {
                self.inner.load()
            }
            fn save(&self, t: &StoredToken) -> Result<(), RpcError> {
                *self.shadow.lock().unwrap() = Some(t.clone());
                self.inner.save(t)
            }
            fn delete(&self) -> Result<(), RpcError> {
                self.inner.delete()
            }
        }
        let _ = store;
        let peek = Box::new(PeekStore {
            shadow: saved_check.clone(),
            inner: InMemoryTokenStore::empty(),
        });

        let svc = make_service(peek, endpoint, "AUTH_CODE");
        let token = svc.login_interactive(crate::progress::noop_auth()).unwrap();
        assert_eq!(token.access_token, "AT");
        assert_eq!(token.refresh_token, "RT");
        let stored = saved_check.lock().unwrap().clone().unwrap();
        assert_eq!(stored.access_token, "AT");
    }

    #[test]
    fn ensure_access_token_returns_cached() {
        let future = Utc::now() + ChronoDuration::hours(1);
        let token = StoredToken {
            client_id: "client-xyz".into(),
            access_token: "CACHED".into(),
            refresh_token: "r".into(),
            access_token_expires_at: future,
            refresh_token_expires_at: future,
            scope: "data:read".into(),
        };
        let store = Box::new(InMemoryTokenStore::preloaded(token));
        let svc = make_service(store, "http://127.0.0.1:1/never".into(), "x");
        let access = svc
            .ensure_access_token(crate::progress::noop_auth())
            .unwrap();
        assert_eq!(access, "CACHED");
    }

    #[test]
    fn ensure_access_token_refreshes_when_expired_but_refresh_valid() {
        let endpoint = spawn_token_endpoint(
            r#"{"access_token":"FRESH","refresh_token":"RT2","expires_in":3600,"refresh_token_expires_in":86400}"#,
        );
        let past = Utc::now() - ChronoDuration::hours(1);
        let future = Utc::now() + ChronoDuration::hours(24);
        let token = StoredToken {
            client_id: "client-xyz".into(),
            access_token: "STALE".into(),
            refresh_token: "OLD_RT".into(),
            access_token_expires_at: past,
            refresh_token_expires_at: future,
            scope: "data:read".into(),
        };
        let store = Box::new(InMemoryTokenStore::preloaded(token));
        let svc = make_service(store, endpoint, "unused");
        let access = svc
            .ensure_access_token(crate::progress::noop_auth())
            .unwrap();
        assert_eq!(access, "FRESH");
    }
}
