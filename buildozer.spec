[app]

title = Secure Vault
package.name = securevault
package.domain = com.offlineapps

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,json,txt
source.exclude_dirs = .git,.github,.buildozer,bin,__pycache__,python-for-android

version = 1.0

# IMPORTANT: Python 3.14 मत उठने दो
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

# IMPORTANT: local stable p4a use करो
p4a.source_dir = ./python-for-android

log_level = 2

[buildozer]
warn_on_root = 1
