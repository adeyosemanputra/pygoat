#!/bin/bash -eux
# ClusterFuzzLite build for Python fuzzers

# Install tools strictly from hashed dev requirements (no ad-hoc pip)
python3 -m pip install --no-cache-dir --require-hashes -r requirements-dev.txt

# Package each fuzz target under fuzz/ into $OUT and add a small wrapper.
for f in $(find fuzz -maxdepth 1 -name 'fuzz_*.py'); do
  base="$(basename -s .py "$f")"
  pyinstaller --clean --distpath "$OUT" --onefile --name "${base}.pkg" "$f"
  cat > "$OUT/$base" << 'EOF'
#!/bin/sh
set -eu
dir="$(dirname "$0")"
exec "$dir/${0##*/}.pkg" "$@"
EOF
  chmod +x "$OUT/$base"
done
