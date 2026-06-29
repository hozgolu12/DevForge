# DevForge CLI Reference Guide

The DevForge Command Line Interface (CLI) provides a unified command set to manage your containers, scaffold new projects, run backups and restores, perform diagnostics, and trigger builds.

---

## 1. Quickstart & Setup

Depending on your shell, you can run either the native Windows PowerShell script or the Bash script.

### Native Windows (PowerShell)
To run the PowerShell CLI, you may need to allow local script execution in your terminal session:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\devforge.ps1 <command> [arguments]
```

### Linux / macOS / Git Bash
```bash
chmod +x devforge
./devforge <command> [arguments]
```

---

## 2. Command Reference

### Service Control

- **`up`**: Starts all platform infrastructure and app containers in the background.
  ```bash
  ./devforge up
  ```
- **`down`**: Stops all active services and releases network ports.
  ```bash
  ./devforge down
  ```
- **`restart [service]`**: Restarts all containers, or a single specified service (e.g. `postgres`, `nginx`).
  ```bash
  ./devforge restart fastapi
  ```
- **`status`**: Displays container states, mapped ports, and health statuses.
  ```bash
  ./devforge status
  ```
- **`logs <service>`**: Streams current log outputs for the target container.
  ```bash
  ./devforge logs mongodb
  ```

---

### Workspace Operations

- **`create <template> <project_name>`**: Generates a new project directory under `projects/` using one of the DevForge templates.
  ```bash
  ./devforge create springboot my-java-api
  ```
  *Supported templates: `react`, `nextjs`, `express`, `nestjs`, `fastapi`, `flask`, `django`, `springboot`, `flutter`, `ai`*
- **`shell <service>`**: Opens an interactive command shell (`zsh`, `bash`, or `sh`) inside the target container.
  ```bash
  ./devforge shell fastapi
  ```
- **`build-apk`**: Compiles the release Android APK target inside the Flutter build environment.
  ```bash
  ./devforge build-apk
  ```

---

### Database Operations

- **`backup`**: Creates snapshot archives of active PostgreSQL, MongoDB, Redis, and Neo4j databases, saving them with timestamps under `backups/`.
  ```bash
  ./devforge backup
  ```
- **`restore <backup_folder_path>`**: Loads database states back from a specified snapshot directory.
  ```bash
  ./devforge restore backups/20260629_120000
  ```
- **`seed`**: Runs SQL, Javascript, CLI pipelines, and Cypher shell scripts to populate databases with starter data.
  ```bash
  ./devforge seed
  ```

---

### System Diagnostics

- **`doctor`**: Conducts health diagnostics:
  - Validates host Docker engine connectivity.
  - Checks Compose configuration syntax.
  - Tests availability of all configured host dev ports (`8080`, `5173`, `8081-8084`, `5050`, `8086-8087`).
  ```bash
  ./devforge doctor
  ```
