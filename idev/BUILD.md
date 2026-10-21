# Soporte iDev — Cómo recompilar

Soporte iDev es RustDesk OSS **1.5.0** (tag `1.5.0`, commit
`fada664df7a294d1d1a9ca3e7cd3637069122f17`, submódulo `libs/hbb_common` en
`229b904508364c8997aad0fb5af57effac859f60`) con un conjunto pequeño de cambios.

- Código fuente: <https://github.com/edbenrio/rustdesk/tree/soporte-idev>
- Workflow: `.github/workflows/soporte-idev-windows.yml`

## Opción A (recomendada): GitHub Actions

Compila en los runners Windows de GitHub, gratis para repos públicos, con las
mismas versiones que el workflow oficial de RustDesk.

1. Hacé un push a la rama `soporte-idev`, o en GitHub abrí **Actions → "Soporte iDev - Windows x64" → Run workflow**.
   Por consola: `gh workflow run "Soporte iDev - Windows x64" -R edbenrio/rustdesk --ref soporte-idev`
2. Esperá a que termine. La primera vez tarda unas 2 horas porque vcpkg compila ffmpeg, libvpx y aom.
   Las siguientes son más rápidas gracias a la caché.
3. Descargá el artefacto `Soporte-iDev-windows-x64`:
   `gh run download <run-id> -R edbenrio/rustdesk -n Soporte-iDev-windows-x64 -D dist`
   Trae `Soporte-iDev.exe`, el zip con la carpeta portable y `SHA256SUMS.txt`.

El workflow corta la compilación si `librustdesk.dll` no trae `rustdesk.idevpy.com`
y la clave pública, o si todavía incluye el servidor público `rs-ny.rustdesk.com`
(lo controla `idev/tools/verify_binary.py`).

## Opción B: compilación local

Hacen falta unos 35 GB libres y las herramientas que figuran en la cabecera de
`idev/build-local.ps1`: VS 2022 Build Tools, LLVM 15.0.6, Rust 1.75,
Flutter 3.24.5 con el motor de rustdesk/engine, vcpkg en el commit fijado y Python.
Después ejecutá:

```powershell
powershell -ExecutionPolicy Bypass -File idev\build-local.ps1
```

> Este script reproduce el workflow, pero **no se probó localmente**: la PC de
> desarrollo tenía solo 17 GB libres. El ejecutable entregado se compiló con la opción A.

## Qué se modificó

| Archivo | Cambio |
|---|---|
| `libs/hbb_common/src/config.rs` (submódulo, lo aplica `idev/tools/apply_hbb_common.py`; está documentado en `idev/patches/hbb_common.patch`) | `APP_NAME = "Soporte-iDev"`; constantes de respaldo `RENDEZVOUS_SERVERS = ["rustdesk.idevpy.com"]` y `RS_PUB_KEY` = clave pública de iDev |
| `src/idev.rs` (nuevo) | Valores predeterminados al arrancar: `custom-rendezvous-server`, `key`, `PROD_RENDEZVOUS_SERVER`, idioma `es` |
| `src/common.rs` | `load_custom_client()` llama a `idev::apply_builtin_defaults()` (lo ejecutan todos los procesos) |
| `src/lib.rs` | registra el módulo `idev` |
| `src/lang.rs`, `src/tray.rs` | textos y tooltip con el nombre visible "Soporte iDev" |
| `flutter/lib/common.dart`, `flutter/lib/main.dart` | título de ventana "Soporte iDev" |
| `flutter/lib/desktop/pages/desktop_setting_page.dart` | enlace al código fuente (AGPL) en "Acerca de" |
| `flutter/windows/runner/Runner.rc`, `libs/portable/Cargo.toml` | metadatos del .exe; se mantiene el copyright de RustDesk |
| Íconos y logos (`res/*.ico`, `res/*.png`, `flutter/windows/runner/resources/app_icon.ico`, `flutter/assets/icon.*`, `flutter/assets/logo*.png`, `libs/portable/src/res/label.png`) | se generan con `idev/tools/make_icons.py` a partir de `idev/branding/idev-logo-source.png` (logo de idevpy.com) |

Sobre el servidor:

- **ID**: `rustdesk.idevpy.com`.
- **Relay**: vacío. hbbs informa su relay automáticamente.
- **API**: vacío. Como es OSS, se deriva `http://rustdesk.idevpy.com:21114`, que es el mismo comportamiento que configurar el cliente a mano.

Estos valores son *predeterminados*: aparecen en **Ajustes → Red → Servidor ID/Relay**
y se pueden editar. Si alguien borra el campo, el cliente vuelve a
`rustdesk.idevpy.com`, nunca a los servidores públicos.

No se usó el mecanismo `custom.txt`, porque exige una firma de RustDesk (Pro).
Tampoco se usó el renombrado del .exe (`rustdesk-host=...`).

## Actualizar a una versión nueva de RustDesk

1. `git fetch https://github.com/rustdesk/rustdesk.git tag <NUEVA>` y luego `git rebase --onto <NUEVA> 1.5.0 soporte-idev`.
2. Si `apply_hbb_common.py` falla, significa que upstream cambió esas líneas. Actualizá `REPLACEMENTS` en el script.
3. Pasá las versiones de `env:` del workflow (Flutter, Rust, LLVM, vcpkg) a las que use el
   `flutter-build.yml` oficial de esa versión, y actualizá `VERSION`.
4. Si cambia el logo, regenerá los íconos con `python idev/tools/make_icons.py` (requiere Pillow).

## Firma digital

El ejecutable **no está firmado**. Por eso Windows SmartScreen va a mostrar
"Windows protegió su PC" hasta que el archivo gane reputación. Para evitarlo hace
falta un certificado de firma de código (OV/EV), que se puede aplicar después con
`signtool sign /fd sha256 /tr http://timestamp.digicert.com /td sha256 Soporte-iDev.exe`.
