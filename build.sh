#!/bin/bash -eux
# ClusterFuzzLite/OSS-Fuzz build script (Python)

# Install build tools strictly from hashed dev requirements
export PIP_NO_CACHE_DIR=1
python3 -m pip install --require-hashes -r requirements-dev.txt

# Package each fuzz target under fuzz/ into $OUT and add a thin wrapper.
for f in $(find fuzz -maxdepth 1 -name 'fuzz_*.py'); do
  base="$(basename -s .py "$f")"
  # Build a self-contained binary
  pyinstaller --clean --distpath "$OUT" --onefile --name "${base}.pkg" "$f"
  # Wrapper that ClusterFuzzLite invokes (binary takes the same args as libFuzzer)
  cat > "$OUT/$base" << 'EOF'
#!/bin/sh
set -eu
dir="$(dirname "$0")"
exec "$dir/${0##*/}.pkg" "$@"
EOF
  chmod +x "$OUT/$base"
done
