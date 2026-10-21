//! Soporte iDev: built-in defaults for this customized RustDesk OSS client.
//!
//! The values are inserted as *defaults* (not overrides), exactly like typing them in
//! "Settings > Network > ID/Relay Server", so they stay visible and editable there.
//! Only the public key of the server is embedded; the private key never leaves the server.

use base::config::keys;
use hbb_common::config;

/// Visible product name. The internal app name (`config::APP_NAME`) is "Soporte-iDev"
/// because install code requires it to match `[a-zA-Z0-9-]+`.
pub const APP_DISPLAY_NAME: &str = "Soporte iDev";
/// ID server (hbbs). The relay (hbbr) is announced by hbbs, so it is left empty.
pub const ID_SERVER: &str = "rustdesk.idevpy.com";
/// Public key of the server (`id_ed25519.pub`).
pub const SERVER_PUBLIC_KEY: &str = "O6qGUkD2hlCk26erLMuMmBk3+PReg03kaXMebv+46G0=";
/// Default UI language.
pub const DEFAULT_LANGUAGE: &str = "es";

/// Must run before any config option is read; called from `load_custom_client()`,
/// which every process (UI, --server, --service, --cm, ...) runs at startup.
pub fn apply_builtin_defaults() {
    // Used when "custom-rendezvous-server" is empty, also for deriving the API server,
    // so an empty field never falls back to public servers.
    *config::PROD_RENDEZVOUS_SERVER.write().unwrap() = ID_SERVER.to_owned();
    {
        let mut settings = config::DEFAULT_SETTINGS.write().unwrap();
        settings
            .entry(keys::OPTION_CUSTOM_RENDEZVOUS_SERVER.to_owned())
            .or_insert_with(|| ID_SERVER.to_owned());
        settings
            .entry(keys::OPTION_KEY.to_owned())
            .or_insert_with(|| SERVER_PUBLIC_KEY.to_owned());
    }
    config::DEFAULT_LOCAL_SETTINGS
        .write()
        .unwrap()
        .entry(keys::OPTION_LANGUAGE.to_owned())
        .or_insert_with(|| DEFAULT_LANGUAGE.to_owned());
}
