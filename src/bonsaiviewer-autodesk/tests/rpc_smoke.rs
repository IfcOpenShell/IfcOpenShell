//! End-to-end smoke test: launch the connector binary and exchange a few
//! JSON-RPC requests over stdin/stdout. Verifies wire-format parity with the
//! Python implementation.

use std::io::{BufRead, BufReader, Write};
use std::process::{Command, Stdio};

use serde_json::Value;

fn binary_path() -> std::path::PathBuf {
    let mut path = std::path::PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    path.push("target");
    path.push(if cfg!(debug_assertions) {
        "debug"
    } else {
        "release"
    });
    path.push(if cfg!(windows) {
        "bonsaiviewer-autodesk.exe"
    } else {
        "bonsaiviewer-autodesk"
    });
    path
}

fn exchange(requests: &[&str]) -> Vec<Value> {
    let path = binary_path();
    assert!(
        path.exists(),
        "expected binary at {}; build with `cargo build --bin bonsaiviewer-autodesk` first",
        path.display()
    );
    let mut child = Command::new(&path)
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .expect("spawn connector binary");
    {
        let stdin = child.stdin.as_mut().expect("stdin");
        for r in requests {
            stdin.write_all(r.as_bytes()).unwrap();
            stdin.write_all(b"\n").unwrap();
        }
        stdin.flush().unwrap();
    }
    // Closing stdin signals EOF; the run loop exits.
    drop(child.stdin.take());

    let stdout = child.stdout.take().expect("stdout");
    let mut reader = BufReader::new(stdout);
    let mut out: Vec<Value> = Vec::new();
    let mut buf = String::new();
    loop {
        buf.clear();
        let n = reader.read_line(&mut buf).unwrap();
        if n == 0 {
            break;
        }
        let trimmed = buf.trim();
        if trimmed.is_empty() {
            continue;
        }
        out.push(serde_json::from_str(trimmed).unwrap());
    }
    let _ = child.wait();
    out
}

#[test]
#[ignore = "requires the binary; run `cargo build --bin bonsaiviewer-autodesk` first"]
fn parse_error_returns_minus_32700() {
    let out = exchange(&["this is not json"]);
    assert_eq!(out.len(), 1);
    assert_eq!(out[0]["error"]["code"], serde_json::json!(-32700));
    assert_eq!(out[0]["id"], serde_json::json!(null));
}

#[test]
#[ignore = "requires the binary; run `cargo build --bin bonsaiviewer-autodesk` first"]
fn unknown_method_returns_minus_32601() {
    let out = exchange(&[r#"{"jsonrpc":"2.0","id":1,"method":"definitely_not_a_method"}"#]);
    assert_eq!(out[0]["error"]["code"], serde_json::json!(-32601));
    assert_eq!(out[0]["id"], serde_json::json!(1));
}

#[test]
#[ignore = "requires the binary; run `cargo build --bin bonsaiviewer-autodesk` first"]
fn invalid_jsonrpc_version_returns_minus_32600() {
    let out = exchange(&[r#"{"id":1,"method":"pull_ifcfed","params":{}}"#]);
    assert_eq!(out[0]["error"]["code"], serde_json::json!(-32600));
}
