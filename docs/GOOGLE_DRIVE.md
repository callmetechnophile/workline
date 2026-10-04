# Google Drive Browser-Based Integration (`wline drive`)
=======================================================
**Specification Version: 1.0**  
**Classification: Storage & Synchronization Workflow**

---

## 1. Overview

WORKLINE integrates with **Google Drive** through a dedicated browser-based workflow (`wline drive`).

> [!IMPORTANT]
> The Google Drive integration does **NOT** use the Google Drive API, Google Cloud Platform service accounts, or OAuth client secrets. It operates entirely through browser automation (`drive.google.com`), honoring the zero-secrets invariant and eliminating GCP project configuration overhead.

---

## 2. Command Reference

All Google Drive operations are invoked through `wline drive`:

```bash
# Launch interactive Google Drive browser workspace
wline drive

# Export current project and upload backup package to Google Drive
wline drive backup

# List available backups and restore a package from Google Drive
wline drive restore
```

---

## 3. Workflow Lifecycle

### 3.1 Backup Workflow (`wline drive backup`)
1. **Local Package Creation:** WORKLINE generates a complete, validated `.wlipjt` or `.workline.zip` archive containing the current `.wl` project state, excluding secrets.
2. **Browser Session Launch:** WORKLINE launches Chromium navigating to `https://drive.google.com`.
3. **Session Check:** If the user is not authenticated, the browser window is displayed for normal Google sign-in.
4. **Automated Upload:** Once authenticated, the browser agent navigates to the dedicated `Workline Projects` folder in the user's Drive and uploads the archive package.
5. **Receipt Generation:** An ArmorIQ receipt with SHA-256 package checksum and upload timestamp is saved locally.

### 3.2 Restore Workflow (`wline drive restore`)
1. **Browser Navigation:** Browser agent accesses the user's Google Drive project folder.
2. **Package Selection:** Locates the specified `.wlipjt` package or lists available timestamped archives.
3. **Download:** Downloads the archive to local staging.
4. **Integrity Verification:** Verifies file hashes against `manifest.wl` inside the archive.
5. **Project Restore:** Unpacks the project into the target directory, verifies zero secrets, and rebuilds the local Moss and Qdrant retrieval indexes.
