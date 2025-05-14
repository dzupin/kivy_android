use debug build to generate signed apk ready to run on android (release must be signed and default is .abb not .apk format)

(.venv3.10) robo@mate40G2024:/QA/kivy_android$ buildozer -v android debug


building and cleaning:
# cleans only specific Android target (recommended)
buildozer android clean
buildozer -v android debug

# more agressive clean that removes entire directroy .buildozer from
buildozer appclean
buildozer -v android debug

# Removes Everything includind SDK, libraries, cached sources
buildozer distclean
buildozer -v android debug
