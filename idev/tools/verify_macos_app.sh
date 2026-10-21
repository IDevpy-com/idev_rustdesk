#!/usr/bin/env bash
# Check a built "Soporte iDev.app" bundle (macOS only).
#
# Usage: idev/tools/verify_macos_app.sh "path/Soporte iDev.app" <x86_64|arm64> <min-macos>
#
# Fails if the bundle name, Info.plist, icon, architecture of any Mach-O file,
# code signature or embedded Soporte iDev configuration are not as expected,
# or if the public RustDesk rendezvous server or key are embedded anywhere.

set -uo pipefail

app=$1
arch=$2
min_macos=$3
root=$(cd "$(dirname "$0")/../.." && pwd)
fail=0

ok() { echo "OK      $*"; }
bad() { echo "FAIL    $*"; fail=1; }

check_eq() { # label actual expected
  if [[ "$2" == "$3" ]]; then ok "$1 = $2"; else bad "$1 = '$2' (expected '$3')"; fi
}

echo "== Bundle: $app (expected arch: $arch, minimum macOS: $min_macos)"
[[ "$(basename "$app")" == "Soporte iDev.app" ]] && ok "bundle name" || bad "bundle name: $(basename "$app")"
[[ -d "$app/Contents/MacOS" ]] || { bad "not an app bundle"; exit 1; }

plist="$app/Contents/Info.plist"
pl() { /usr/libexec/PlistBuddy -c "Print :$1" "$plist" 2>/dev/null; }
echo "== Info.plist"
plutil -lint "$plist" || fail=1
check_eq CFBundleName "$(pl CFBundleName)" "Soporte iDev"
check_eq CFBundleDisplayName "$(pl CFBundleDisplayName)" "Soporte iDev"
check_eq CFBundleIdentifier "$(pl CFBundleIdentifier)" "com.idevpy.soporte"
check_eq CFBundleExecutable "$(pl CFBundleExecutable)" "Soporte-iDev"
check_eq CFBundlePackageType "$(pl CFBundlePackageType)" "APPL"
check_eq CFBundleIconFile "$(pl CFBundleIconFile)" "AppIcon.icns"
check_eq LSMinimumSystemVersion "$(pl LSMinimumSystemVersion)" "$min_macos"
check_eq "CFBundleURLSchemes:0" "$(pl 'CFBundleURLTypes:0:CFBundleURLSchemes:0')" "soporte-idev"
echo "CFBundleShortVersionString = $(pl CFBundleShortVersionString), CFBundleVersion = $(pl CFBundleVersion)"
echo "NSHumanReadableCopyright = $(pl NSHumanReadableCopyright)"

echo "== Icon"
icon="$app/Contents/Resources/AppIcon.icns"
if [[ -f "$icon" ]] && cmp -s "$icon" "$root/flutter/macos/Runner/AppIcon.icns"; then
  ok "AppIcon.icns is the Soporte iDev icon ($(shasum -a 256 "$icon" | cut -d' ' -f1))"
else
  bad "AppIcon.icns missing or not the Soporte iDev icon"
fi

echo "== Executables and libraries"
exe="$app/Contents/MacOS/Soporte-iDev"
[[ -f "$exe" ]] && ok "main executable" || bad "main executable missing"
[[ -f "$app/Contents/MacOS/service" ]] && ok "service helper" || bad "service helper missing"
dylib="$app/Contents/Frameworks/liblibrustdesk.dylib"
[[ -f "$dylib" ]] && ok "liblibrustdesk.dylib" || bad "liblibrustdesk.dylib missing"

max_minos=0.0
while IFS= read -r -d '' f; do
  file -b "$f" | grep -q 'Mach-O' || continue
  archs=$(lipo -archs "$f" 2>/dev/null)
  minos=$(otool -l "$f" 2>/dev/null | awk '/LC_BUILD_VERSION/{b=1} b&&$1=="minos"{print $2; exit} /LC_VERSION_MIN_MACOSX/{v=1} v&&$1=="version"{print $2; exit}')
  rel=${f#"$app/"}
  case "$rel" in
    Contents/MacOS/*|Contents/Frameworks/liblibrustdesk.dylib)
      # Our own binaries must be thin and of the target architecture.
      [[ "$archs" == "$arch" ]] && ok "$rel: $archs, minos $minos" || bad "$rel: '$archs' (expected '$arch')";;
    *)
      [[ " $archs " == *" $arch "* ]] && ok "$rel: $archs, minos $minos" || bad "$rel: '$archs' lacks $arch";;
  esac
  if [[ -n "$minos" ]] && [[ "$(printf '%s\n%s\n' "$max_minos" "$minos" | sort -V | tail -1)" == "$minos" ]]; then
    max_minos=$minos
  fi
done < <(find "$app/Contents" -type f -print0)
echo "Highest minos of all Mach-O files: $max_minos (LSMinimumSystemVersion: $min_macos)"
if [[ "$(printf '%s\n%s\n' "$max_minos" "$min_macos" | sort -V | tail -1)" != "$min_macos" ]]; then
  bad "a binary requires macOS $max_minos, newer than LSMinimumSystemVersion $min_macos"
fi

echo "== Linked libraries of the main executable"
otool -L "$exe" | sed 's/^/        /'

echo "== Embedded Soporte iDev configuration"
python3 "$root/idev/tools/verify_binary.py" "$dylib" || fail=1
for s in "rs-ny.rustdesk.com" "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw="; do
  hits=$(grep -rlF "$s" "$app" 2>/dev/null)
  [[ -z "$hits" ]] && ok "'$s' absent in the whole bundle" || bad "'$s' found in: $hits"
done

echo "== License files"
for f in LICENSES/RustDesk-AGPL-3.0.txt LICENSES/NOTICE.txt; do
  [[ -s "$app/Contents/Resources/$f" ]] && ok "Resources/$f" || bad "Resources/$f missing"
done

echo "== Code signature"
if codesign --verify --deep --strict --verbose=2 "$app"; then ok "codesign --verify --deep --strict"; else bad "invalid code signature"; fi
codesign -dvv "$app" 2>&1 | grep -E '^(Identifier|Format|CodeDirectory|Signature|Authority|TeamIdentifier|Runtime)' | sed 's/^/        /'
ents=$(codesign -d --entitlements :- "$app" 2>/dev/null)
echo "$ents" | grep -q 'com.apple.security.device.audio-input' && ok "entitlements embedded" || bad "entitlements missing"
echo "$ents" | grep -q 'com.apple.security.cs.disable-library-validation' && bad "library validation disabled" || ok "library validation not disabled"

echo
if [[ $fail -eq 0 ]]; then echo "RESULT: PASS"; else echo "RESULT: FAIL"; fi
exit $fail
