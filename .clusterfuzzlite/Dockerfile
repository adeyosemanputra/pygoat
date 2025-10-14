FROM gcr.io/oss-fuzz-base/base-builder-python

# Copy the whole repo to /src so /src/build.sh exists
COPY . $SRC
WORKDIR $SRC

# Ensure build.sh is executable (web edits don't set +x)
RUN chmod +x $SRC/build.sh || true
