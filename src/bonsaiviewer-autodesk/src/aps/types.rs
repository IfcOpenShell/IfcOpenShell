use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Hub {
    pub id: String,
    pub name: String,
    pub extension_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Project {
    pub id: String,
    pub name: String,
    pub extension_type: String,
    pub root_folder_id: String,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize, PartialEq, Eq)]
#[serde(rename_all = "lowercase")]
pub enum EntryType {
    Folders,
    Items,
    #[serde(other)]
    Other,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Entry {
    pub id: String,
    #[serde(rename = "type")]
    pub entry_type: EntryType,
    pub display_name: String,
    pub name: Option<String>,
    pub extension_type: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ItemTip {
    pub id: String,
    pub display_name: String,
    pub hidden: bool,
    pub version_id: Option<String>,
    pub storage_id: Option<String>,
    pub version_number: Option<serde_json::Value>,
    pub last_modified_time_utc: Option<String>,
    pub last_modified_user_name: Option<String>,
    pub parent_folder_id: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct UploadResult {
    pub item_id: String,
    pub version_id: String,
    pub display_name: String,
    pub version_number: Option<serde_json::Value>,
    pub last_modified_time_utc: Option<String>,
    pub last_modified_user_name: Option<String>,
}
