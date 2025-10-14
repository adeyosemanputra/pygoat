#!/bin/bash -eux
# Install your app (only needed if you ship C-exts; harmless otherwise)
# pip3 install .

# Build Python fuzzers into $OUT as standalone binaries and wrappers (per OSS-Fuzz guidance)
for fuzzer in $(find $SRC -name 'fuzz_*.py'); do
  fbase=$(basename -s .py "$fuzzer")
  pkg="${fbase}.pkg"
  pyinstaller --distpath "$OUT" --onefile --name "$pkg" "$fuzzer"
  # Wrapper that executes the packaged fuzzer with the right env
  cat > "$OUT/$fbase" << 'EOF'
#!/bin/sh
this_dir="$(dirname "$0")"
# For pure-Python targets, omit LD_PRELOAD to avoid sanitizer issues.
exec "$this_dir/${0##*/}.pkg" "$@"
EOF
  chmod +x "$OUT/$fbase"
done
