#!/bin/bash -eux
# ClusterFuzzLite/OSS-Fuzz build script (Python)

# Tools needed to package Python fuzzers for libFuzzer runner
python3 -m pip install --no-cache-dir -U pip
python3 -m pip install --no-cache-dir atheris==2.3.0 pyinstaller==6.9.0

# Build each fuzz target under fuzz/ into $OUT and add a thin wrapper.
# Example target: fuzz/fuzz_parseqs.py  (add more fuzz_*.py files as you like)
for fuzzer in $(find fuzz -maxdepth 1 -name 'fuzz_*.py'); do
  base="$(basename -s .py "$fuzzer")"
  # Build a self-contained binary
  pyinstaller --clean --distpath "$OUT" --onefile --name "${base}.pkg" "$fuzzer"
  # Wrapper that ClusterFuzzLite invokes (binary takes the same args as libFuzzer)
  cat > "$OUT/$base" << 'EOF'
#!/bin/sh
set -eu
dir="$(dirname "$0")"
exec "$dir/${0##*/}.pkg" "$@"
EOF
  chmod +x "$OUT/$base"
done
