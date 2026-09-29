pub mod browse;
pub mod transfer;
pub mod types;

use std::sync::Arc;
use std::time::Duration;

use crate::auth::AuthSessionService;

pub use types::{Entry, EntryType, Hub, ItemTip, Project, UploadResult};

pub struct ApsClient {
    pub(crate) auth: Arc<AuthSessionService>,
    pub(crate) agent: ureq::Agent,
    pub(crate) base_url: String,
}

impl ApsClient {
    pub fn new(auth: Arc<AuthSessionService>) -> Self {
        Self::with_base_url(auth, "https://developer.api.autodesk.com".into())
    }

    pub fn with_base_url(auth: Arc<AuthSessionService>, base_url: String) -> Self {
        Self {
            auth,
            agent: ureq::AgentBuilder::new()
                .timeout(Duration::from_secs(120))
                .build(),
            base_url,
        }
    }
}
