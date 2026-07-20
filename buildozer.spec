[app]

title = Secure Vault
package.name = securevault
package.domain = com.offlineapps

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,ttf,atlas,txt
source.exclude_dirs = .buildozer,.git,bin,__pycache__,.github

version = 1.0

# ✅ Simple requirements - no extra dependencies
requirements = python3,kivy

orientation = portrait
fullscreen = 0

# ─── Android Settings ───
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a

# ─── Permissions ───
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,VIBRATE

# ─── SDK ───
android.accept_sdk_license = True
android.skip_update = True

# ─── Build ───
log_level = 2
p4a.branch = develop

[buildozer]
warn_on_root = 1
