# Soporte iDev para macOS — Cómo recompilar

Soporte iDev para macOS es el mismo código que la versión Windows (RustDesk OSS
**1.5.0**, tag `1.5.0`, commit `fada664df7a294d1d1a9ca3e7cd3637069122f17`,
submódulo `libs/hbb_common` en `229b904508364c8997aad0fb5af57effac859f60`) más
unos pocos cambios propios de macOS. Ver también `BUILD.md` (Windows).

- Código fuente: <https://github.com/edbenrio/idev_rustdesk/tree/soporte-idev>
- Workflow: `.github/workflows/build-macos.yml` ("Soporte iDev - macOS")
- Build entregado: ver `INFORME-macOS.md` (commit, run y SHA-256).

## Compilar con GitHub Actions

1. En GitHub: **Actions → "Soporte iDev - macOS" → Run workflow** (rama `soporte-idev`).
   Por consola:
   `gh workflow run build-macos.yml -R edbenrio/idev_rustdesk --ref soporte-idev -f launch-test=true`
2. El workflow compila las dos arquitecturas en paralelo, cada una en un runner nativo:

   | Paquete | Target Rust | Runner | Features | macOS mínimo |
   |---|---|---|---|---|
   | `Soporte-iDev-macOS-Intel.dmg` | `x86_64-apple-darwin` | `macos-15-intel` | `flutter,hwcodec,unix-file-copy-paste` | 10.14 |
   | `Soporte-iDev-macOS-AppleSilicon.dmg` | `aarch64-apple-darwin` | `macos-14` | `flutter,hwcodec,unix-file-copy-paste,screencapturekit` | 12.3 |

3. Descargá el artefacto `Soporte-iDev-macOS` (los dos `.dmg` y `SHA256SUMS.txt`):
   `gh run download <run-id> -R edbenrio/idev_rustdesk -n Soporte-iDev-macOS -D dist`
   Los artefactos `logs-macOS-Intel` y `logs-macOS-AppleSilicon` traen las
   verificaciones, el log de la prueba de lanzamiento y una captura de pantalla.

La opción `launch-test` abre la app en el runner unos 40 segundos. En ese tiempo
la app se conecta a `rustdesk.idevpy.com` y registra un ID efímero, igual que
cualquier cliente. Se puede desactivar al lanzar el workflow.

### Qué hace el workflow

Reproduce el job oficial `build-for-macOS` de `flutter-build.yml` de la 1.5.0, con
las mismas versiones, y agrega los pasos de Soporte iDev:

1. Aplica `idev/tools/apply_hbb_common.py` (APP_NAME, servidor y clave en `hbb_common`).
2. Instala `llvm`, `create-dmg` y `pkg-config` (Homebrew), NASM 2.16.03 (nasm.us),
   Flutter 3.24.5 (con el parche oficial del dropdown y el workaround del issue 133533),
   Rust 1.81 (lo exige `cidre`) y las dependencias de `vcpkg.json` con vcpkg en `9e593bb1`.
   El puente flutter_rust_bridge sale de `bridge.yml`, igual que en Windows.
3. Para arm64 sube el deployment target a 12.3 (necesario para ScreenCaptureKit), igual que el workflow oficial.
4. `python3 build.py --flutter --hwcodec --unix-file-copy-paste [--screencapturekit]`.
5. Copia `Soporte-iDev.app` como **`Soporte iDev.app`** y agrega
   `Contents/Resources/LICENSES/` (AGPL-3.0 de RustDesk y `NOTICE.txt`).
6. Firma: ad-hoc (`-`) con `.github/scripts/sign-macos-app.sh` (runtime endurecido y
   `Release.entitlements`). Hace falta incluso sin certificado: `build.py` copia el
   helper `service` después de que Xcode firmó el bundle, lo que rompe el sello.
7. `idev/tools/verify_macos_app.sh`: nombre del bundle, `Info.plist`, ícono,
   arquitectura de **cada** Mach-O, `minos` máximo frente a `LSMinimumSystemVersion`,
   servidor y clave embebidos, ausencia de `rs-ny.rustdesk.com` y de la clave pública
   oficial en todo el bundle, licencias y firma.
8. Crea el DMG con `create-dmg` (app, acceso directo a Aplicaciones y `LEAME.txt`),
   lo verifica con `hdiutil verify`, lo monta y repite la verificación sobre la app del DMG.
9. Prueba de lanzamiento (ver arriba) y SHA-256.

## Cambios propios de macOS

| Archivo | Cambio |
|---|---|
| `flutter/macos/Runner/Configs/AppInfo.xcconfig` | `PRODUCT_NAME = Soporte-iDev` (nombre del ejecutable = APP_NAME interno), `PRODUCT_MODULE_NAME = RustDesk` (lo referencia `MainMenu.xib`), copyright con atribución a RustDesk |
| `flutter/macos/Runner.xcodeproj/project.pbxproj` | `PRODUCT_BUNDLE_IDENTIFIER = com.idevpy.soporte` |
| `flutter/macos/Runner/Info.plist` | `CFBundleName` y `CFBundleDisplayName` = "Soporte iDev"; esquema URL `soporte-idev` (= `get_uri_prefix()`); texto del micrófono en español |
| `flutter/macos/Runner/Base.lproj/MainMenu.xib` | Barra de menús en español ("Acerca de Soporte iDev", "Salir de Soporte iDev", Edición, Visualización, Ventana, Ayuda) |
| `flutter/macos/Runner/AppIcon.icns`, `res/mac-icon.png`, `res/mac-tray-*.png` | Íconos generados con `idev/tools/make_macos_icons.py` desde `idev/branding/idev-logo-source.png` |
| `build.py` (`build_flutter_dmg`) | Copia `service` a `Soporte-iDev.app` en lugar de `RustDesk.app` |
| `idev/LICENSES/NOTICE.txt` | Ubicación de los avisos de Flutter también en macOS |
| `.github/workflows/build-macos.yml`, `idev/tools/verify_macos_app.sh`, `idev/README-macOS.txt` | Nuevos |

Todo lo demás (servidor, clave, idioma, nombre visible en Flutter, "Acerca de",
íconos de Flutter) es el código multiplataforma que ya usa Windows. Ningún cambio
toca archivos que compile Windows, salvo `build.py` dentro de la función exclusiva de macOS.

### Nombres y por qué

| Qué | Valor |
|---|---|
| Carpeta de la app | `Soporte iDev.app` |
| Nombre visible (menú, Dock, Finder, Ajustes del Sistema) | `Soporte iDev` |
| Ejecutable (`CFBundleExecutable`) | `Soporte-iDev` |
| Identificador de paquete | `com.idevpy.soporte` |
| Configuración del usuario | `~/Library/Preferences/com.carriez.Soporte-iDev/` |
| Logs | `~/Library/Logs/Soporte-iDev/` |

El código de RustDesk arma rutas como `/Applications/<APP_NAME>.app/Contents/MacOS/<APP_NAME>`
para el servicio de launchd y la autoactualización. Por eso el ejecutable conserva
el nombre interno `Soporte-iDev`, igual que en Windows. La carpeta se llama
`Soporte iDev.app` y, en consecuencia, RustDesk nunca considera la app "instalada":
no muestra la tarjeta "Instalar" del servicio (daemon/LaunchAgent) ni ofrece
actualizarse. Así queda en el modo que se pidió: el servidor de escritorio remoto
corre solo dentro de la app abierta, sin servicios persistentes, sin inicio
automático y sin acceso desatendido. Si en el futuro se quisiera ofrecer el modo
instalado, habría que distribuir la carpeta como `Soporte-iDev.app`.

El prefijo `com.carriez` de la carpeta de configuración y de las etiquetas de
launchd viene de `ORG` en `hbb_common`; no se cambió para no alterar el código común
con Windows. No es visible para el usuario.

## Firma, notarización y permisos

- **Sin cuenta de Apple Developer** el workflow firma ad-hoc. Gatekeeper avisa la
  primera vez y el usuario autoriza la app desde Ajustes del Sistema →
  Privacidad y seguridad → "Abrir igualmente" (ver `README-macOS.txt`).
  No se usa `xattr`, `spctl --master-disable` ni ninguna otra forma de evitar Gatekeeper.
- Con firma ad-hoc, macOS asocia los permisos (Grabación de pantalla, Accesibilidad,
  Monitoreo de entrada) al hash del ejecutable: **cada versión nueva pide autorizar
  los permisos otra vez**. Con firma Developer ID se conservan entre versiones.
- **Firma Developer ID y notarización (preparadas, no probadas):** crear estos
  secretos en *Settings → Secrets and variables → Actions* del repositorio:

  | Secreto | Contenido |
  |---|---|
  | `MACOS_P12_BASE64` | certificado "Developer ID Application" exportado como `.p12`, en base64 |
  | `MACOS_P12_PASSWORD` | contraseña del `.p12` |
  | `MACOS_CODESIGN_IDENTITY` | p. ej. `Developer ID Application: iDev (ABCDE12345)` |
  | `MACOS_NOTARY_APPLE_ID`, `MACOS_NOTARY_TEAM_ID`, `MACOS_NOTARY_PASSWORD` | Apple ID, Team ID y contraseña específica de app para `notarytool` |

  Con `MACOS_P12_BASE64` presente, el workflow firma la app con esa identidad
  (con sello de tiempo), firma el DMG y, si están los secretos `MACOS_NOTARY_*`,
  lo notariza y engrapa el ticket. Sin secretos, todo sigue funcionando con firma ad-hoc.

## Compilar en una Mac (opcional, no probado)

Requiere Xcode, Homebrew, Rust 1.81, Flutter 3.24.5 y vcpkg en `9e593bb1`
(`VCPKG_ROOT` definido). Desde la raíz del repo, en una Mac de la arquitectura deseada:

```sh
git submodule update --init --recursive
python3 idev/tools/apply_hbb_common.py
brew install llvm create-dmg pkg-config
$VCPKG_ROOT/vcpkg install --x-install-root="$VCPKG_ROOT/installed"
# generar el puente (ver .github/workflows/bridge.yml) o copiar bridge-artifact
python3 build.py --flutter --hwcodec --unix-file-copy-paste      # Apple Silicon: agregar --screencapturekit
ditto flutter/build/macos/Build/Products/Release/Soporte-iDev.app "out/Soporte iDev.app"
bash .github/scripts/sign-macos-app.sh "out/Soporte iDev.app" - flutter/macos/Runner/Release.entitlements
```

## Universal (x86_64 + arm64)

No se generó. Sería posible unir con `lipo` los binarios Rust y el ejecutable de
ambos builds, pero las dos arquitecturas no comparten configuración: arm64 usa
ScreenCaptureKit y requiere macOS 12.3, Intel admite 10.14. Un universal obligaría
a elegir un único mínimo o a renunciar a ScreenCaptureKit, por lo que se priorizaron
dos paquetes independientes.

## Regenerar íconos

```sh
python idev/tools/make_macos_icons.py   # requiere Pillow; no modifica los íconos de Windows
```
