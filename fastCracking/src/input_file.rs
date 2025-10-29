use anyhow::Result;
use memmap2::Mmap;
use std::{fs::File, path::Path};

pub struct MmapLines {
    buf: Mmap,
    idx: Vec<usize>, // line start positions
    pos: usize,
}

impl MmapLines {
    pub fn open<P: AsRef<Path>>(p: P) -> Result<Self> {
        let file = File::open(p)?;
        let buf = unsafe { Mmap::map(&file)? };
        let mut idx = Vec::with_capacity(1024);
        idx.push(0);
        for (i, &b) in buf.iter().enumerate() {
            if b == b'\n' { idx.push(i + 1); }
        }
        if *idx.last().unwrap_or(&0) != buf.len() { idx.push(buf.len()); }
        Ok(Self { buf, idx, pos: 0 })
    }

    /// Resume from line offset
    pub fn seek_line(&mut self, line: usize) { self.pos = self.pos.max(line).min(self.idx.len().saturating_sub(1)); }

    pub fn total_lines(&self) -> usize { self.idx.len().saturating_sub(1) }

    /// Get slice for line `i` trimmed of ascii ws/CRLF
    pub fn line_at(&self, i: usize) -> &[u8] {
        let start = self.idx[i];
        let end = self.idx[i+1];
        trim(&self.buf[start..end])
    }

    pub fn range(&self) -> std::ops::Range<usize> { 0..self.total_lines() }
}

#[inline] fn is_ws(b: u8) -> bool { matches!(b, b' ' | b'\t' | b'\r' | b'\n') }
#[inline] fn trim(s: &[u8]) -> &[u8] {
    let mut a = 0; let mut b = s.len();
    while a < b && is_ws(s[a]) { a+=1; }
    while b > a && is_ws(s[b-1]) { b-=1; }
    &s[a..b]
}
