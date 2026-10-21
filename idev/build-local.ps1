# Soporte iDev - compilación local en Windows x64 (equivalente a
# .github/workflows/soporte-idev-windows.yml). Requiere ~35 GB libres.
#
# Requisitos previos (fuentes oficiales):
#   - Visual Studio 2022 Build Tools con "Desarrollo de escritorio con C++" y Windows 10/11 SDK
#   - LLVM 15.0.6 (https://github.com/llvm/llvm-project/releases/tag/llvmorg-15.0.6), LIBCLANG_PATH configurado
#   - Rust 1.75 vía rustup:  rustup toolchain install 1.75-x86_64-pc-windows-msvc; rustup default 1.75
#   - Flutter 3.24.5 (no otra versión) + motor de rustdesk/engine + parche dropdown (ver workflow)
#   - vcpkg en el commit 9e593bb18ea69cc5095e012465dcd675a822ed0d, VCPKG_ROOT configurado
#   - Python 3, Git, 7-Zip
#   - El "bridge" de flutter_rust_bridge 1.80.1 generado (ver .github/workflows/bridge.yml)
#
# Uso, desde la raíz del repositorio:
#   powershell -ExecutionPolicy Bypass -File idev\build-local.ps1

$ErrorActionPreference = 'Stop'
$AppExe = 'Soporte-iDev.exe'
$Root = (Resolve-Path "$PSScriptRoot\..").Path
Set-Location $Root

python idev\tools\apply_hbb_common.py
if ($LASTEXITCODE -ne 0) { throw 'apply_hbb_common.py failed' }

& "$env:VCPKG_ROOT\vcpkg.exe" install --triplet x64-windows-static --x-install-root="$env:VCPKG_ROOT\installed"
if ($LASTEXITCODE -ne 0) { throw 'vcpkg install failed' }

python build.py --portable --flutter --skip-portable-pack --hwcodec --vram
if ($LASTEXITCODE -ne 0) { throw 'build.py failed' }

$Out = Join-Path $Root 'rustdesk'
if (Test-Path $Out) { Remove-Item -Recurse -Force $Out }
Move-Item flutter\build\windows\x64\runner\Release $Out

python idev\tools\verify_binary.py "$Out\librustdesk.dll"
if ($LASTEXITCODE -ne 0) { throw 'verify_binary.py failed' }

Move-Item "$Out\rustdesk.exe" "$Out\$AppExe"
New-Item -ItemType Directory -Force "$Out\LICENSES" | Out-Null
Copy-Item LICENCE "$Out\LICENSES\RustDesk-AGPL-3.0.txt"
Copy-Item idev\LICENSES\NOTICE.txt "$Out\LICENSES\NOTICE.txt"

(Get-Content res\manifest.xml) | Where-Object { $_ -notmatch 'dpiAware' } | Set-Content res\manifest.xml -Encoding utf8
Push-Location libs\portable
pip install -r requirements.txt
python generate.py -f ..\..\rustdesk\ -o . -e "..\..\rustdesk\$AppExe"
Pop-Location
git checkout -- res\manifest.xml

New-Item -ItemType Directory -Force dist | Out-Null
$Packer = @('target\release\rustdesk-portable-packer.exe', 'libs\portable\target\release\rustdesk-portable-packer.exe') |
    Where-Object { Test-Path $_ } | Select-Object -First 1
Move-Item -Force $Packer "dist\$AppExe"
Get-FileHash "dist\$AppExe" -Algorithm SHA256 | Format-List
