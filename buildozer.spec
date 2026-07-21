[app]

# Application title
title = AppLock Security

# Package name
package.name = applock

# Package domain
package.domain = org.test

# Version codes
version = 1.0
requirements = python3, kivy==2.2.1, pyjnius

# Source directories and extensions
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json

# Application entry point
source.main_dir = .
source.main_file = main.py

# Android-specific settings
android.permissions = INTERNET, USE_BIOMETRIC, USE_FINGERPRINT, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, SYSTEM_ALERT_WINDOW, PACKAGE_USAGE_STATS
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

# Buildozer settings
android.accept_sdk_license = True
p4a.branch = master

# Services (if needed later)
services = 

# Build settings
android.add_compile_options = 
android.add_gradle_repositories = 
android.gradle_dependencies = 
android.presplash_color = #FFFFFF
android.uses_sdl2 = True
android.private_storage = True

[buildozer]

# Log level (0 = error, 1 = warning, 2 = info, 3 = debug)
log_level = 2

# Directory to store build artifacts
bin_dir = bin

# Directory to store temporary build files
build_dir = .buildozer
