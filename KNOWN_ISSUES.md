# Known Issues and Solutions

**This document outlines known issues in PyGoat and their solutions.**

---

## SQLite Database File Permissions (Linux/macOS)

### Issue
When running PyGoat via Docker on Linux or macOS, the `db.sqlite3` file is created with `root:root` ownership. This can cause permission issues when trying to delete or modify the database file from the host system.

**Example:**
```bash
$ ls -la db.sqlite3
-rw-r--r-- 1 root root 339968 Dec 26 22:21 db.sqlite3
```

### Why This Happens
Docker containers run as the root user by default. When Django creates the SQLite database file inside the container, it inherits root ownership, which persists on the host filesystem due to the volume mount.

### Solutions

#### Solution 1: Use `sudo` for File Operations (Quick Fix)
When you need to delete or modify the database file on the host:

```bash
sudo rm db.sqlite3
# or
sudo chown $USER:$USER db.sqlite3
```

#### Solution 2: Run Containers as Non-Root User (Recommended for Development)
Modify `docker-compose.yml` to run containers with your user ID:

```yaml
services:
  migration:
    # ... existing config ...
    user: "${UID:-1000}:${GID:-1000}"
  
  web:
    # ... existing config ...
    user: "${UID:-1000}:${GID:-1000}"
```

Then update the `Dockerfile` to set proper permissions:

```dockerfile
# Add before EXPOSE
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
```

**Note:** This approach requires rebuilding containers and may need adjustments based on your system's UID/GID.

#### Solution 3: Fix Permissions After Stopping Containers
After running `docker compose down`, fix permissions:

```bash
docker compose down
sudo chown -R $USER:$USER .
```

#### Solution 4: Use Named Volume (Production Recommendation)
For production deployments, consider using a named Docker volume instead of a bind mount:

```yaml
services:
  migration:
    volumes:
      - .:/app
      - db_data:/app/db.sqlite3

volumes:
  db_data:
```

This isolates the database file within Docker's managed storage.

### Recommendation
- **For local development:** Use Solution 1 (sudo) or Solution 2 (non-root user)
- **For production:** Use Solution 4 (named volume)
- **For CI/CD:** This issue typically doesn't affect automated pipelines

---

## Contributing

If you encounter other issues, please report them via [GitHub Issues](https://github.com/adeyosemanputra/pygoat/issues).