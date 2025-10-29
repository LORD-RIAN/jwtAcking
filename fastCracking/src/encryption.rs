use anyhow::{anyhow, bail, Context, Result};
use base64::{engine::general_purpose::URL_SAFE_NO_PAD, Engine as _};
use ring::hmac;

#[derive(Clone, Copy, Debug)]
pub enum HsAlg { HS256, HS384, HS512 }

impl HsAlg {
    fn ring(self) -> hmac::Algorithm {
        match self {
            HsAlg::HS256 => hmac::HMAC_SHA256,
            HsAlg::HS384 => hmac::HMAC_SHA384,
            HsAlg::HS512 => hmac::HMAC_SHA512,
        }
    }
}

/// Return (signing_input_bytes, signature_bytes)
pub fn parse_jwt(token: &str) -> Result<(Box<[u8]>, Vec<u8>)> {
    let mut parts = token.split('.');
    let h = parts.next().context("missing header")?;
    let p = parts.next().context("missing payload")?;
    let s = parts.next().context("missing signature")?;
    if parts.next().is_some() { bail!("too many dots"); }

    // "header.payload" as raw bytes
    let mut signing = Vec::with_capacity(h.len() + 1 + p.len());
    signing.extend_from_slice(h.as_bytes());
    signing.push(b'.');
    signing.extend_from_slice(p.as_bytes());

    // base64url (no pad) decode → map error into anyhow
    let sig = URL_SAFE_NO_PAD
        .decode(s.as_bytes())
        .map_err(|e| anyhow!("base64url signature decode failed: {e}"))?;

    Ok((signing.into_boxed_slice(), sig))
}

/// Constant-time verify via ring::hmac::verify (no deprecated API)
#[inline]
pub fn hmac_matches(alg: HsAlg, key: &[u8], signing_input: &[u8], sig: &[u8]) -> bool {
    let k = hmac::Key::new(alg.ring(), key);
    hmac::verify(&k, signing_input, sig).is_ok()
}
