[app]

# ─────────────────────────────
# App Basic Info
# ─────────────────────────────
title = Secure Vault
package.name = securevault
package.domain = com.offlineapps

# ─────────────────────────────
# Source Files
# ─────────────────────────────
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,ttf,atlas,txt

# ─────────────────────────────
# Version
# ─────────────────────────────
version = 1.0

# ─────────────────────────────
# Requirements
# ─────────────────────────────
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,cryptography

# ─────────────────────────────
# Display
# ─────────────────────────────
orientation = portrait
fullscreen = 0

# ─────────────────────────────
# Icons & Splash
# ─────────────────────────────
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png
presplash.color = #000000

# ─────────────────────────────
# Android Settings
# ─────────────────────────────
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a

# ─────────────────────────────
# Android Permissions
# App Locker के लिए जरूरी
# ─────────────────────────────
android.permissions = \
    INTERNET, \
    READ_EXTERNAL_STORAGE, \
    WRITE_EXTERNAL_STORAGE, \
    MANAGE_EXTERNAL_STORAGE, \
    
