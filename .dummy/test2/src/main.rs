use serde::{Deserialize, Serialize};
use std::fs::{self, OpenOptions};
use std::io::{BufWriter, Write};
use std::path::Path;
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::time::Instant;

const ALPHABET: &[u8] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
const RADIX: u128 = 52;

#[inline]
fn idx_to_word(mut idx: u128, len: usize, out: &mut [u8]) {
    for pos in (0..len).rev() {
        let digit = (idx % RADIX) as usize;
        out[pos] = ALPHABET[digit];
        idx /= RADIX;
    }
}

#[derive(Debug, Clone)]
pub struct ComboChunker {
    min_len: usize,
    max_len: usize,
    chunk_size: usize,

    cur_len: usize,
    cur_idx: u128,
    cur_end: u128,
    finished: bool,
}

impl ComboChunker {
    pub fn new(min_len: usize, max_len: usize, chunk_size: usize) -> Self {
        assert!(min_len >= 1 && max_len >= min_len, "invalid length range");
        assert!(chunk_size > 0, "chunk_size must be > 0");
        let cur_end = RADIX.pow(min_len as u32) as u128;
        Self {
            min_len,
            max_len,
            chunk_size,
            cur_len: min_len,
            cur_idx: 0,
            cur_end,
            finished: false,
        }
    }

    pub fn total_space(&self) -> u128 {
        let mut total: u128 = 0;
        for l in self.min_len..=self.max_len {
            total += RADIX.pow(l as u32) as u128;
        }
        total
    }

    /// Build a chunk and advance internal state. Returns None when finished.
    pub fn next_chunk(&mut self) -> Option<Vec<Vec<u8>>> {
        if self.finished {
            return None;
        }

        let mut chunk = Vec::with_capacity(self.chunk_size);

        while chunk.len() < self.chunk_size {
            if self.cur_idx >= self.cur_end {
                if self.cur_len >= self.max_len {
                    self.finished = true;
                    break;
                }
                self.cur_len += 1;
                self.cur_idx = 0;
                self.cur_end = RADIX.pow(self.cur_len as u32) as u128;
            }

            if self.finished {
                break;
            }

            let mut buf = vec![0u8; self.cur_len];
            idx_to_word(self.cur_idx, self.cur_len, &mut buf);
            chunk.push(buf);

            self.cur_idx += 1;
        }

        if chunk.is_empty() {
            None
        } else {
            Some(chunk)
        }
    }
}

fn write_chunk_to_file(path: &str, chunk: &[Vec<u8>]) -> std::io::Result<u64> {
    let file = OpenOptions::new().create(true).append(true).open(path)?;
    let mut writer = BufWriter::new(file);
    let mut written: u64 = 0;

    for word in chunk {
        writer.write_all(word)?;
        writer.write_all(b"\n")?;
        written += word.len() as u64 + 1; // +1 for newline
    }

    writer.flush()?;
    Ok(written)
}

#[derive(Serialize, Deserialize, Debug)]
struct Checkpoint {
    cur_len: usize,
    cur_idx: u128,
    cur_end: u128,
    total_bytes: u64,
    produced: u128,
    file_index: u32,
    min_len: usize,
    max_len: usize,
    chunk_size: usize,
}

fn save_checkpoint_atomic(cp: &Checkpoint, path: &str) -> std::io::Result<()> {
    let tmp = format!("{}.tmp", path);
    let json = serde_json::to_vec_pretty(cp).unwrap();
    fs::write(&tmp, &json)?;
    fs::rename(tmp, path)?;
    Ok(())
}

fn load_checkpoint(path: &str) -> Option<Checkpoint> {
    match fs::read_to_string(path) {
        Ok(s) => serde_json::from_str(&s).ok(),
        Err(_) => None,
    }
}

fn main() -> std::io::Result<()> {
    // Config
    let min_len = 1usize;
    let max_len = 5usize;
    let chunk_size = 10_000usize;
    let per_file_byte_cap: u64 = 3000 * 1024 * 1024; // rotate file after this many bytes
    let checkpoint_path = "checkpoint.json";
    let pause_sentinel = Path::new("PAUSE"); // create this file to request pause
    let mut file_index: u32 = 1;

    // Interruption flag
    let running = Arc::new(AtomicBool::new(true));
    {
        let r = running.clone();
        ctrlc::set_handler(move || {
            eprintln!("\nSIGINT received -> graceful shutdown requested.");
            r.store(false, Ordering::SeqCst);
        })
        .expect("Error setting Ctrl-C handler");
    }

    // Try load checkpoint
    let mut total_bytes: u64 = 0;
    let mut produced: u128 = 0;
    let mut gen = ComboChunker::new(min_len, max_len, chunk_size);

    if let Some(cp) = load_checkpoint(checkpoint_path) {
        eprintln!("Loaded checkpoint: {:?}", cp);
        // restore state
        let mut restored = gen;
        restored.cur_len = cp.cur_len;
        restored.cur_idx = cp.cur_idx;
        restored.cur_end = cp.cur_end;
        restored.finished = false;
        gen = restored;
        total_bytes = cp.total_bytes;
        produced = cp.produced;
        file_index = cp.file_index;
    } else {
        println!("No checkpoint found; starting fresh.");
    }

    println!("Total theoretical space: {}", gen.total_space());
    let start_time = Instant::now();

    while running.load(Ordering::SeqCst) {
        // If user asked for pause (create PAUSE file), then save checkpoint and exit.
        if pause_sentinel.exists() {
            let cp = Checkpoint {
                cur_len: gen.cur_len,
                cur_idx: gen.cur_idx,
                cur_end: gen.cur_end,
                total_bytes,
                produced,
                file_index,
                min_len,
                max_len,
                chunk_size,
            };
            save_checkpoint_atomic(&cp, checkpoint_path)?;
            println!("PAUSE sentinel detected. Checkpoint saved to {}. Exiting.", checkpoint_path);
            return Ok(());
        }

        match gen.next_chunk() {
            Some(chunk) => {
                let out_name = format!("output_{:04}.txt", file_index);
                let written = write_chunk_to_file(&out_name, &chunk)?;
                total_bytes += written;
                produced += chunk.len() as u128;

                // Report progress occasionally
                if produced % (chunk_size as u128 * 10) == 0 {
                    println!(
                        "Wrote {} bytes into {} (total bytes: {}, combos produced: {})",
                        written, out_name, total_bytes, produced
                    );
                }

                // Rotate file when per-file cap reached
                if total_bytes >= per_file_byte_cap {
                    // save checkpoint using the *next* indices (we already advanced cur_idx)
                    let cp = Checkpoint {
                        cur_len: gen.cur_len,
                        cur_idx: gen.cur_idx,
                        cur_end: gen.cur_end,
                        total_bytes: 0, // reset per-file counter for next file
                        produced,
                        file_index: file_index + 1,
                        min_len,
                        max_len,
                        chunk_size,
                    };
                    save_checkpoint_atomic(&cp, checkpoint_path)?;
                    println!(
                        "Per-file byte cap reached ({} bytes). Rotating file. Checkpoint saved to {}.",
                        total_bytes, checkpoint_path
                    );
                    // prepare for next file
                    file_index += 1;
                    total_bytes = 0;
                    // Exit so that the user can inspect or restart — this is the "stop and wait" behavior.
                    println!("Exiting after rotation. Rerun the program to continue from the checkpoint.");
                    return Ok(());
                }

                // graceful immediate-exit if requested
                if !running.load(Ordering::SeqCst) {
                    let cp = Checkpoint {
                        cur_len: gen.cur_len,
                        cur_idx: gen.cur_idx,
                        cur_end: gen.cur_end,
                        total_bytes,
                        produced,
                        file_index,
                        min_len,
                        max_len,
                        chunk_size,
                    };
                    save_checkpoint_atomic(&cp, checkpoint_path)?;
                    println!("Graceful shutdown: checkpoint saved to {}.", checkpoint_path);
                    return Ok(());
                }
            }
            None => {
                println!("Enumeration finished (all combos generated). Removing checkpoint (if any).");
                if Path::new(checkpoint_path).exists() {
                    let _ = fs::remove_file(checkpoint_path);
                }
                println!("Done. combos produced: {}. elapsed: {:?}", produced, start_time.elapsed());
                return Ok(());
            }
        }
    }

    Ok(())
}
