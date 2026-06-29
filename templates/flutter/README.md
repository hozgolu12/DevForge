# DevForge Flutter Template

Production-grade Flutter project template for DevForge.

## Structure
- `lib/`: Flutter/Dart application code.
- `android/`: Android platform configuration and Gradle setup.

## Execution & Compilation
Build the Android APK inside the container:
```bash
docker compose exec flutter flutter build apk --release
```
