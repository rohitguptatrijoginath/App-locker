[app]

title = Secure Vault
package.name = securevault
package.domain = com.offlineapps

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt
source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__

version = 1.0

# Fixed: Remove explicit python/kivy version pinning to avoid recipe crashes
requirements = python3,kivy

orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a

android.permissions = INTERNET,VIBRATE

android.accept_sdk_license = True
android.skip_update = False

log_level = 2

[buildozer]
warn_on_root = 1
