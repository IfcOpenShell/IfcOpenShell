use std::rc::Rc;

use bonsaiviewer_autodesk::connector::AutodeskConnector;
use bonsaiviewer_autodesk::rpc::JsonRpcHost;
use bonsaiviewer_autodesk::ui;

fn main() {
    // FLTK must be initialised on the main thread before any widget is
    // touched. We do it eagerly here so RPC handlers can open dialogs
    // without a cold-start race.
    let _app = ui::ensure_app();

    let connector = Rc::new(AutodeskConnector::new());
    let handlers = connector.handlers();
    let mut host = JsonRpcHost::new(handlers, std::io::stdin().lock(), std::io::stdout().lock());
    std::process::exit(host.run());
}
