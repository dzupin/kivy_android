use debug build to generate signed apk ready to run on android (release must be signed and default is .abb not .apk format)

(.venv3.10) robo@mate40G2024:/QA/kivy_android$ buildozer -v android debug


building and cleaning:
# cleans only specific Android target (recommended) - safe to use
buildozer android clean
buildozer -v android debug

# more agressive clean that removes entire directroy .buildozer from  - safe to use
buildozer appclean
buildozer -v android debug

# Removes Everything includind SDK, libraries, cached sources
WARNING: it will break your SDK environment and you will have to manually deploy it again (automatic re-deployment will fail)
buildozer distclean
buildozer -v android debug


FIX:
for missing Android API 31 error, after using 'buildozer distclean' and then trying to run: buildozer -v android debug
use .vemv3.10 in Pycharm
(.venv3.10) robo@mate40G2024:/QA/kivy_android$
INSTRUCTION that worked:
    Identify the Missing API Level:
    Note the API level from the Buildozer error message (e.g., 31).

    Navigate to the sdkmanager Directory:
    Open your terminal and type:
    cd ~/.buildozer/android/platform/android-sdk/tools/bin/

    Install the Required SDK Platform:
    Execute the sdkmanager command. Replace 31 with your required API level.
    ./sdkmanager --sdk_root=~/.buildozer/android/platform/android-sdk "platforms;android-31"
    Wait for it to complete.

    Install Corresponding Build Tools (Recommended):
    ./sdkmanager --sdk_root=~/.buildozer/android/platform/android-sdk "build-tools;31.0.0"
    (Use a build-tools version like 31.0.0 for API 31).

    Accept SDK Licenses:
    ./sdkmanager --sdk_root=~/.buildozer/android/platform/android-sdk --licenses
    Review and accept all licenses (type y and press Enter).

    Return to Your Kivy Project Directory:
    Navigate back to your Kivy application's root directory.
    cd /QA/kivy_android
    (e.g., cd /QA/kivy_android)

    Retry the Buildozer Build Command:
    buildozer -v android debug