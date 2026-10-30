// Rebuild when embedded content or the harness changes; include_dir! does not track new files.
fn main() {
    println!("cargo:rerun-if-changed=content");
    println!("cargo:rerun-if-changed=harness");
}
