#!/bin/bash
# Usage: chunkpull.sh <package> <outdir>
# Pulls an APK in 4 MB chunks with retries (survives short USB resets).
# Temp chunks live in /sdcard/zt_tmp on the car and are deleted afterwards.
pkg="$1"; out="$2"; CH=4  # MB per chunk
w() { for i in $(seq 1 30); do adb get-state >/dev/null 2>&1 && return 0; sleep 1; done; return 1; }
run() { for t in 1 2 3 4 5 6; do w || continue; r=$(adb shell "$1" 2>/dev/null | tr -d '\r') && [ -n "$r" ] && { echo "$r"; return 0; }; done; return 1; }

path=$(run "pm path $pkg" | sed 's/package://' | head -1) || { echo "nopath $pkg"; exit 1; }
size=$(run "stat -c %s $path") || exit 1
full=$(run "md5sum $path" | cut -d' ' -f1) || exit 1
n=$(( (size + CH*1048576 - 1) / (CH*1048576) ))
tmp=$(mktemp -d /tmp/cp.XXXX)
run "mkdir -p /sdcard/zt_tmp && echo ok" >/dev/null
for ((i=0;i<n;i++)); do
  for t in 1 2 3 4 5 6 7 8; do
    w || continue
    want=$(adb shell "dd if=$path of=/sdcard/zt_tmp/c bs=1048576 skip=$((i*CH)) count=$CH 2>/dev/null; md5sum /sdcard/zt_tmp/c" 2>/dev/null | tr -d '\r' | cut -d' ' -f1)
    [ -z "$want" ] && continue
    adb pull /sdcard/zt_tmp/c "$tmp/$i" >/dev/null 2>&1 || continue
    [ "$(md5 -q "$tmp/$i")" = "$want" ] && break
  done
  [ -f "$tmp/$i" ] || { echo "FAIL chunk $i $pkg"; exit 1; }
done
run "rm -rf /sdcard/zt_tmp && echo ok" >/dev/null
for ((i=0;i<n;i++)); do cat "$tmp/$i"; done > "$out/$pkg.apk"
[ "$(md5 -q "$out/$pkg.apk")" = "$full" ] && echo "ok $pkg ($n chunks)" || { echo "MD5 MISMATCH $pkg"; rm -f "$out/$pkg.apk"; }
