[app]
title = JarvisAI
package.name = jarvisai
package.domain = com.jarvis.ai
source.dir = .
source.include_exts = py,png,jpg,kv,txt
version = 1.0
requirements = python3,kivy==2.3.0,requests,urllib3,chardet,idna,certifi,pyjnius,android
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,RECORD_AUDIO,ACCESS_NETWORK_STATE
android.api = 33
android.minapi = 24
android.archs = arm64-v8a
android.allow_backup = True
android.accept_sdk_license = True
p4a.branch = master
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
