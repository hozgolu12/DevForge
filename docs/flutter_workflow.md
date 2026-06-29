# DevForge Flutter Platform Workflow Guide

This document provides guidelines and commands for building Flutter mobile applications inside the DevForge environment, connecting to physical devices via Android Debug Bridge (ADB), and deploying applications.

---

## 1. APK Build Workflow

DevForge isolates the Flutter SDK and Android SDK in the `flutter` container, allowing you to compile your apps to Android APKs without installing SDKs on your host machine.

### Build Steps

1. **Start the Flutter Container** (Ensure it is running):
   ```bash
   docker compose up -d flutter
   ```

2. **Trigger Compilation**:
   From the host machine, compile the release APK:
   ```bash
   make flutter-build-apk
   # Or run manually:
   # docker compose exec flutter flutter build apk --release
   ```

3. **Locate Build Output**:
   The output APK will be available in your project workspace on the host:
   `projects/<your-app-name>/build/app/outputs/flutter-apk/app-release.apk`

---

## 2. ADB Guidance (Android Debug Bridge)

Since physical USB devices cannot easily pass through to the Docker container on Windows/macOS hosts, we recommend running ADB directly on the **host machine** to bridge the built APK to your device.

### Installing ADB on Host

- **Windows**: Download [SDK Platform-Tools for Windows](https://developer.android.com/tools/releases/platform-tools) and extract it (e.g. to `C:\platform-tools`). Add this folder to your system PATH.
- **Mac**: Install via Homebrew: `brew install android-platform-tools`
- **Linux**: Install via apt: `sudo apt-get install android-tools-adb`

---

## 3. Physical Device Workflow

Follow these steps to deploy and test the release APK on a physical Android device:

### Step 1: Enable USB Debugging on Android Device
1. Open **Settings** on your phone.
2. Go to **About Phone** and tap **Build Number** 7 times to enable Developer Options.
3. Return to Settings -> System -> **Developer Options**.
4. Enable **USB Debugging**.

### Step 2: Connect via USB
1. Connect your phone to your host computer via a USB cable.
2. Verify the host detects the device:
   ```bash
   adb devices
   ```
   *(Ensure you authorize the connection popup prompt on your phone's screen).*

### Step 3: Install APK
Deploy the compiled release APK to your connected device:
```bash
adb install projects/sample-flutter/build/app/outputs/flutter-apk/app-release.apk
```

### Step 4: (Alternative) Wireless Debugging (Over Wi-Fi)
If you prefer wireless connections:
1. Ensure both your computer and phone are connected to the same Wi-Fi network.
2. Find your phone's IP address (e.g., Settings -> About Status -> IP address).
3. Connect using TCP:
   ```bash
   adb tcpip 5555
   adb connect <device-ip-address>:5555
   ```
4. Unplug the USB cable and verify:
   ```bash
   adb devices
   ```
