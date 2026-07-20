[app]

title = Secure Vault
package.name = securevault
package.domain = com.offlineapps

source.dir = .
source.include_exts = py,png,jpg,kv

version = 1.0

requirements = python3,kivy

orientation = portrait
fullscreen = 0

icon.filename = icon.png

android.api = 31
android.minapi = 21
android.ndk_api = 21
android.ndk = 25b
android.archs = arm64-v8a

android.accept_sdk_license = True
android.skip_update = False

log_level = 2

[buildozer]
warn_on_root = 1
