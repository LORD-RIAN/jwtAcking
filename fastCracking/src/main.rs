mod input_file;
mod encryption;

use anyhow::Result;
use clap::{Parser, ValueEnum};
use input_file::MmapLines;
use rayon::prelude::*;
use encryption::{parse_jwt, hmac_matches, HsAlg};

#[derive(Debug, Clone, Copy, ValueEnum)]
enum Alg { HS256, HS384, HS512 }
impl From<Alg> for HsAlg {
    fn from(a: Alg) -> HsAlg {
        match a {
            Alg::HS256 => HsAlg::HS256,
            Alg::HS384 => HsAlg::HS384,
            Alg::HS512 => HsAlg::HS512,
        }
    }
}

#[derive(Parser, Debug)]
#[command(version, about = "Ultra-fast HS* JWT checker (authorized use only)")]
struct Args {
    /// JWT (header.payload.signature)
    token: String,
    /// Wordlist path (huge files OK)
    wordlist: String,
    /// Algorithm to verify
    #[arg(long, value_enum, default_value_t = Alg::HS256)]
    alg: Alg,
    /// Start from line offset (resume)
    #[arg(long, default_value_t = 0usize)]
    start_at: usize,
    /// Threads (default: all cores)
    #[arg(long)]
    threads: Option<usize>,
}

fn main() -> Result<()> {
    let args = Args::parse();

    if let Some(t) = args.threads {
        rayon::ThreadPoolBuilder::new().num_threads(t).build_global().ok();
    }

    let (signing, sig) = parse_jwt(&args.token)?;
    let mut mm = MmapLines::open(&args.wordlist)?;
    if args.start_at > 0 { mm.seek_line(args.start_at); }

    eprintln!(
        "[*] lines≈{}, starting at {}, alg={:?}",
        mm.total_lines(), args.start_at, args.alg
    );

    let alg = HsAlg::from(args.alg);
    let signing = &*signing; // &[u8]
    let sig = &*sig;

    // Parallel search across line indices; zero-copy candidate slices.
    let found = mm.range().into_par_iter().find_map_any(|i| {
        let cand = mm.line_at(i);
        if cand.is_empty() { return None; }
        if hmac_matches(alg, cand, signing, sig) {
            Some(String::from_utf8_lossy(cand).into_owned())
        } else { None }
    });

    match found {
        Some(secret) => println!("[+] MATCH: {secret}"),
        None => println!("[-] No match in this list/range."),
    }
    Ok(())
}
