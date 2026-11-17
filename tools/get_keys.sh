#!/bin/bash
# Downloads the PUBLIC AOSP test platform key (build/target/product/security in AOSP) into keys/.
# The head unit runs a test-keys build, so the manager app must be signed with this key to get
# the system uid (android.uid.system) needed to install and toggle overlays.
# This key is public knowledge; it is not a secret and gives no access to anything else.
set -e
DIR="$(cd "$(dirname "$0")/.." && pwd)/keys"; mkdir -p "$DIR"
BASE="https://android.googlesource.com/platform/build/+/refs/heads/main/target/product/security"
for f in platform.pk8 platform.x509.pem; do
  curl -sfL "$BASE/$f?format=TEXT" | base64 --decode > "$DIR/$f"
done
echo "Cert SHA-1 (expect 27:19:6E:38:6B:87:5E:76:AD:F7:00:E7:EA:84:E4:C6:EE:E3:3D:FA):"
openssl x509 -in "$DIR/platform.x509.pem" -noout -fingerprint -sha1
