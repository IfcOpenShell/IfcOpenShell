use std::collections::HashMap;
use std::io::{BufRead, BufReader, Read, Write};

use serde_json::{json, Value};

pub const JSONRPC_PARSE_ERROR: i32 = -32700;
pub const JSONRPC_INVALID_REQUEST: i32 = -32600;
pub const JSONRPC_METHOD_NOT_FOUND: i32 = -32601;
pub const JSONRPC_INVALID_PARAMS: i32 = -32602;
pub const JSONRPC_INTERNAL_ERROR: i32 = -32603;

#[derive(Debug, Clone)]
pub struct RpcError {
    pub code: i32,
    pub message: String,
    pub data: Option<Value>,
}

impl RpcError {
    pub fn new(code: i32, message: impl Into<String>) -> Self {
        Self { code, message: message.into(), data: None }
    }

    pub fn internal(message: impl Into<String>) -> Self {
        Self::new(JSONRPC_INTERNAL_ERROR, message)
    }

    pub fn invalid_params(message: impl Into<String>) -> Self {
        Self::new(JSONRPC_INVALID_PARAMS, message)
    }
}

impl std::fmt::Display for RpcError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.message)
    }
}

impl std::error::Error for RpcError {}

pub type Handler = Box<dyn Fn(Value) -> Result<Value, RpcError>>;

pub struct JsonRpcHost<R: Read, W: Write> {
    handlers: HashMap<String, Handler>,
    stdin: BufReader<R>,
    stdout: W,
}

impl<R: Read, W: Write> JsonRpcHost<R, W> {
    pub fn new(handlers: HashMap<String, Handler>, stdin: R, stdout: W) -> Self {
        Self { handlers, stdin: BufReader::new(stdin), stdout }
    }

    pub fn run(&mut self) -> i32 {
        let mut line = String::new();
        loop {
            line.clear();
            match self.stdin.read_line(&mut line) {
                Ok(0) => return 0,
                Ok(_) => {}
                Err(_) => return 0,
            }
            let trimmed = line.trim().to_string();
            if trimmed.is_empty() {
                continue;
            }
            self.handle_line(&trimmed);
        }
    }

    fn handle_line(&mut self, line: &str) {
        let message: Value = match serde_json::from_str(line) {
            Ok(v) => v,
            Err(e) => {
                self.respond_error(Value::Null, JSONRPC_PARSE_ERROR, &format!("Parse error: {e}"), None);
                return;
            }
        };

        let obj = match message.as_object() {
            Some(o) => o,
            None => {
                self.respond_error(Value::Null, JSONRPC_INVALID_REQUEST, "Request must be a JSON object", None);
                return;
            }
        };

        let message_id = obj.get("id").cloned().unwrap_or(Value::Null);

        if obj.get("jsonrpc").and_then(|v| v.as_str()) != Some("2.0") {
            self.respond_error(message_id, JSONRPC_INVALID_REQUEST, "Missing or wrong 'jsonrpc' version", None);
            return;
        }

        let method = match obj.get("method").and_then(|v| v.as_str()) {
            Some(m) => m.to_string(),
            None => {
                self.respond_error(message_id, JSONRPC_INVALID_REQUEST, "Missing 'method' string", None);
                return;
            }
        };

        let params = obj.get("params").cloned().unwrap_or(Value::Null);
        if !params.is_null() && !params.is_object() && !params.is_array() {
            self.respond_error(message_id, JSONRPC_INVALID_PARAMS, "'params' must be a JSON object or array", None);
            return;
        }

        let outcome = match self.handlers.get(&method) {
            Some(handler) => handler(params),
            None => {
                self.respond_error(message_id, JSONRPC_METHOD_NOT_FOUND, &format!("Unknown method '{method}'"), None);
                return;
            }
        };

        match outcome {
            Ok(result) => {
                if !message_id.is_null() {
                    self.respond_result(message_id, result);
                }
            }
            Err(err) => {
                eprintln!("Handler '{method}' raised: {}", err.message);
                self.respond_error(message_id, err.code, &err.message, err.data);
            }
        }
    }

    fn respond_result(&mut self, id: Value, result: Value) {
        let payload = json!({"jsonrpc": "2.0", "id": id, "result": result});
        self.write(&payload);
    }

    fn respond_error(&mut self, id: Value, code: i32, message: &str, data: Option<Value>) {
        let mut error = json!({"code": code, "message": message});
        if let Some(d) = data {
            error.as_object_mut().unwrap().insert("data".into(), d);
        }
        let payload = json!({"jsonrpc": "2.0", "id": id, "error": error});
        self.write(&payload);
    }

    fn write(&mut self, payload: &Value) {
        let line = serde_json::to_string(payload).unwrap_or_else(|_| "{}".into());
        let _ = self.stdout.write_all(line.as_bytes());
        let _ = self.stdout.write_all(b"\n");
        let _ = self.stdout.flush();
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn run_once(handlers: HashMap<String, Handler>, input: &str) -> Vec<Value> {
        let mut buf: Vec<u8> = Vec::new();
        {
            let mut host = JsonRpcHost::new(handlers, input.as_bytes(), &mut buf);
            host.run();
        }
        let text = String::from_utf8(buf).unwrap();
        text.lines()
            .filter(|l| !l.trim().is_empty())
            .map(|l| serde_json::from_str::<Value>(l).unwrap())
            .collect()
    }

    fn echo_handlers() -> HashMap<String, Handler> {
        let mut m: HashMap<String, Handler> = HashMap::new();
        m.insert("echo".into(), Box::new(|p| Ok(p)));
        m.insert("boom".into(), Box::new(|_| Err(RpcError::internal("bang"))));
        m.insert("bad_params".into(), Box::new(|_| Err(RpcError::invalid_params("nope"))));
        m
    }

    #[test]
    fn dispatches_result() {
        let out = run_once(echo_handlers(), "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"echo\",\"params\":{\"x\":1}}\n");
        assert_eq!(out.len(), 1);
        assert_eq!(out[0]["result"], json!({"x": 1}));
        assert_eq!(out[0]["id"], json!(1));
    }

    #[test]
    fn notification_no_response() {
        let out = run_once(echo_handlers(), "{\"jsonrpc\":\"2.0\",\"method\":\"echo\",\"params\":{}}\n");
        assert!(out.is_empty());
    }

    #[test]
    fn unknown_method() {
        let out = run_once(echo_handlers(), "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"nope\"}\n");
        assert_eq!(out[0]["error"]["code"], json!(JSONRPC_METHOD_NOT_FOUND));
    }

    #[test]
    fn parse_error_yields_null_id() {
        let out = run_once(echo_handlers(), "not json\n");
        assert_eq!(out[0]["error"]["code"], json!(JSONRPC_PARSE_ERROR));
        assert_eq!(out[0]["id"], json!(null));
    }

    #[test]
    fn missing_jsonrpc_version() {
        let out = run_once(echo_handlers(), "{\"id\":1,\"method\":\"echo\"}\n");
        assert_eq!(out[0]["error"]["code"], json!(JSONRPC_INVALID_REQUEST));
    }

    #[test]
    fn invalid_params_shape() {
        let out = run_once(echo_handlers(), "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"echo\",\"params\":42}\n");
        assert_eq!(out[0]["error"]["code"], json!(JSONRPC_INVALID_PARAMS));
    }

    #[test]
    fn handler_error_passes_code() {
        let out = run_once(echo_handlers(), "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"bad_params\"}\n");
        assert_eq!(out[0]["error"]["code"], json!(JSONRPC_INVALID_PARAMS));
        assert_eq!(out[0]["error"]["message"], json!("nope"));
    }

    #[test]
    fn multiple_lines_processed() {
        let out = run_once(
            echo_handlers(),
            "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"echo\",\"params\":{}}\n\n{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"echo\",\"params\":[]}\n",
        );
        assert_eq!(out.len(), 2);
        assert_eq!(out[0]["id"], json!(1));
        assert_eq!(out[1]["id"], json!(2));
    }
}
