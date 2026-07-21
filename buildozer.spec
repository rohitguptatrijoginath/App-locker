# ===== buildozer.spec =====
[App]

title = Secure Vault
package.name = securevault
package.domain = com.offlineapps

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt
source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__,python-for-android

version = 1.0

# Python 3.11 + Kivy 2.3 stable
requirements = python3==3.11.7,kivy==2.3.0

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a

android.permissions = INTERNET,VIBRATE

android.accept_sdk_license = True
android.skip_update = True

# use local python-for-android
p4a.source_dir = ./python-for-android

log_level = 2

[buildozer]
warn_on_root = 1


# ===== .github/workflows/build.yml =====
name: Build Secure Vault APK

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
          cache: "pip"

      - name: Setup Java 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: "17"

      - name: Install system dependencies
        shell: bash
        run: |
          sudo apt-get update
          sudo apt-get install -y             git zip unzip autoconf libtool pkg-config             zlib1g-dev libncurses5-dev libncursesw5-dev             cmake libffi-dev libssl-dev python3-dev             build-essential libsqlite3-dev ccache             libltdl-dev libbz2-dev liblzma-dev lld

      - name: Install Python packages
        shell: bash
        run: |
          set -eux
          python -m pip install --upgrade pip setuptools wheel
          python -m pip install Cython==0.29.37
          python -m pip install buildozer==1.5.0

      - name: Restore buildozer cache
        uses: actions/cache@v4
        with:
          path: |
            ~/.buildozer
            .buildozer
          key: buildozer-${{ runner.os }}-${{ hashFiles('buildozer.spec') }}
          restore-keys: |
            buildozer-${{ runner.os }}-

      - name: Clone stable python-for-android
        shell: bash
        run: |
          set -eux
          if [ ! -d "python-for-android" ]; then
            git clone --depth 1 --branch 2024.01.21 https://github.com/kivy/python-for-android.git python-for-android
          fi

      - name: Prepare Android SDK
        shell: bash
        run: |
          set -euxo pipefail
          SDK=/usr/local/lib/android/sdk
          SDKMGR=$(find "$SDK/cmdline-tools" -name sdkmanager -type f | head -1)

          sudo mkdir -p "$SDK/tools/bin"
          sudo ln -sf "$SDKMGR" "$SDK/tools/bin/sdkmanager"

          yes | "$SDKMGR" --licenses || true

          "$SDKMGR" --sdk_root="$SDK"             "platform-tools"             "platforms;android-33"             "build-tools;33.0.2"             "ndk;25.2.9519653"

          echo "ANDROID_HOME=$SDK" >> "$GITHUB_ENV"
          echo "ANDROID_SDK_ROOT=$SDK" >> "$GITHUB_ENV"
          echo "ANDROIDSDK=$SDK" >> "$GITHUB_ENV"
          echo "ANDROIDNDK=$SDK/ndk/25.2.9519653" >> "$GITHUB_ENV"
          echo "ANDROID_NDK_HOME=$SDK/ndk/25.2.9519653" >> "$GITHUB_ENV"

          echo "$SDK/build-tools/33.0.2" >> "$GITHUB_PATH"
          echo "$SDK/platform-tools" >> "$GITHUB_PATH"

      - name: Build APK
        shell: bash
        run: |
          set -euxo pipefail
          buildozer -v android debug 2>&1 | tee build.log
        env:
          ANDROIDSDK: ${{ env.ANDROIDSDK }}
          ANDROIDNDK: ${{ env.ANDROIDNDK }}
          ANDROID_HOME: ${{ env.ANDROID_HOME }}
          ANDROID_SDK_ROOT: ${{ env.ANDROID_SDK_ROOT }}
          ANDROID_NDK_HOME: ${{ env.ANDROID_NDK_HOME }}
          ANDROIDAPI: "33"
          ANDROIDMINAPI: "21"
          NDKAPI: "21"
          BUILDOZER_ALLOW_ORG_NAME_START: "1"

      - name: Upload build log
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: Build-Log
          path: build.log

      - name: Upload APK
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: Secure-Vault-APK
          path: bin/*.apk
          if-no-files-found: warn

