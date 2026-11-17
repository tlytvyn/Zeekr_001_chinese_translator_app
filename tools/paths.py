"""Shared paths for all build tools.

REPO  - this repository (translations, app source, signing keys).
WORK  - working directory for proprietary inputs and build outputs that are NOT
        committed: apks/ (original Zeekr APKs), dec/ (apktool output), build/, dist/.
        Override with ZEEKR_WORK (default: ~/zeekr_tr).
SDK   - Android SDK. Override with ANDROID_HOME / ANDROID_SDK_ROOT.
BT    - build-tools dir. Override with ZEEKR_BUILD_TOOLS (default: newest installed).
JAR   - android.jar used for linking. Override with ZEEKR_ANDROID_JAR.
"""
import glob
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.path.expanduser(os.environ.get("ZEEKR_WORK", "~/zeekr_tr"))
SDK = os.path.expanduser(os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
                         or "~/Library/Android/sdk")


def _newest_build_tools():
    dirs = sorted(glob.glob(f"{SDK}/build-tools/*"),
                  key=lambda p: [int(x) if x.isdigit() else 0 for x in os.path.basename(p).split(".")])
    return dirs[-1] if dirs else f"{SDK}/build-tools/36.1.0"


BT = os.path.expanduser(os.environ.get("ZEEKR_BUILD_TOOLS") or _newest_build_tools())
JAR = os.path.expanduser(os.environ.get("ZEEKR_ANDROID_JAR") or f"{SDK}/platforms/android-30/android.jar")
KEY, CERT = f"{REPO}/keys/platform.pk8", f"{REPO}/keys/platform.x509.pem"
