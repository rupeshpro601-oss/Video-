# VS Code Mobile — prebuilt debug APK

A ready-to-install debug build of [r987r/Vs-code-mobile](https://github.com/r987r/Vs-code-mobile)
("VS Code Mobile — GitHub Codespaces on Android"), built from upstream `main`
(commit `ee315c1`) exactly as described in its README:

- Built with: Gradle 8.4 / AGP 8.2.2 / Kotlin 1.9.22 / compileSdk 34 / JDK 17
- Command: `./gradlew assembleDebug`
- Unit tests and Android Lint: passed
- Package: `com.vscode.mobile.debug` · versionName `1.0.0` (versionCode 1)
- Requires Android 8.0 (API 26) or later

## Files

- `app-debug.apk` — the installable debug APK
- `app-debug.apk.sha256` — integrity checksum

## Verify the checksum

```bash
sha256sum -c app-debug.apk.sha256
# Expected: app-debug.apk: OK
```

## Install on your phone

1. Enable **Settings → Apps → (your file manager) → Install unknown apps → Allow**.
2. Transfer `app-debug.apk` to your phone (USB, Drive, email — any method).
3. Open the file and tap **Install**.
4. Launch **VS Code Mobile**, sign in to GitHub in the WebView, and your codespaces appear.
