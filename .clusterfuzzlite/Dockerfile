FROM gcr.io/oss-fuzz-base/base-builder-python@sha256:e29848e799e0e448ae8fd281a439c58b2ef1ca0d89117f4def43385d278c5655

# Copy the whole repo to /src so /src/build.sh exists
COPY . $SRC
WORKDIR $SRC

# Ensure build.sh is executable (web edits don't set +x)
RUN chmod +x $SRC/build.sh || true
