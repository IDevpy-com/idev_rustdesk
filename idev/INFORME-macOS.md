# Informe: Soporte iDev para macOS (Intel y Apple Silicon)

Fecha: 23/10/2026

## Resultado

Se generaron los dos instaladores. Ambos compilaron en GitHub Actions y pasaron
todas las verificaciones automáticas, incluida una prueba de lanzamiento en un
runner macOS real de cada arquitectura.

```
SHA-256  c01da03eef8036e2886818bc917c861945d5849d04a838c99e4b0e1e3b7c910d  Soporte-iDev-macOS-Intel.dmg
SHA-256  c42df318e81ec03e7f0755c2339b5a045cd7f348d7a927b18ddf1b7d69bfd26e  Soporte-iDev-macOS-AppleSilicon.dmg
```

| Paquete | Para | macOS mínimo | Arquitectura |
|---|---|---|---|
| `Soporte-iDev-macOS-Intel.dmg` | Mac con procesador Intel | 10.14 Mojave | x86_64 |
| `Soporte-iDev-macOS-AppleSilicon.dmg` | Mac con chip Apple M1/M2/M3/M4… | 12.3 Monterey | arm64 |

Cada `.dmg` contiene `Soporte iDev.app`, un acceso directo a Aplicaciones y `LEAME.txt`
(instrucciones para el cliente, igual a `README-macOS.txt`).

**No están firmados con certificado de Apple ni notarizados** (firma ad-hoc).
macOS muestra un aviso la primera vez y el cliente debe autorizar la app desde
Ajustes del Sistema → Privacidad y seguridad (ver `README-macOS.txt`).

## Versión del código

- Base: RustDesk OSS **1.5.0**, commit `fada664df7a294d1d1a9ca3e7cd3637069122f17`;
  `libs/hbb_common` en `229b904508364c8997aad0fb5af57effac859f60`.
- Rama `soporte-idev`. Los dos paquetes **provienen de commits distintos**:

  | Paquete | Commit | Run |
  |---|---|---|
  | Intel | `09e571150` (final) | <https://github.com/edbenrio/rustdesk/actions/runs/39694268515> |
  | Apple Silicon | `c417345a4` | <https://github.com/edbenrio/rustdesk/actions/runs/39686850912> |

  `09e5711` solo agrega, respecto de `c417345`, la traducción de los menús Edición /
  Visualización / Ventana / Ayuda y la prueba de cierre del workflow. El código Rust,
  la configuración del servidor, el bundle ID y los íconos son idénticos.
  El build de Apple Silicon sobre `09e5711` falló por un error de red del runner
  (`git clone` de un paquete Flutter cortado con "Connection reset by peer") y no se
  pudo relanzar porque GitHub respondió "Actions has been disabled for this repository"
  (ver Limitaciones). Cuando Actions vuelva a funcionar, conviene regenerar Apple Silicon
  desde `09e5711` para que ambos paquetes salgan del mismo commit.
- Ambos commits incluyen todos los cambios de Windows sin modificarlos; la compilación
  Windows se volvió a ejecutar con éxito sobre los dos (runs 39686844559 y 39694268262).

## Herramientas y dependencias

Las mismas del job oficial `build-for-macOS` de RustDesk 1.5.0:

| Componente | Versión / origen |
|---|---|
| Runner Intel | `macos-15-intel` (GitHub) |
| Runner Apple Silicon | `macos-14` (GitHub) |
| Rust | 1.81 (rustup, `dtolnay/rust-toolchain`) |
| Flutter | 3.24.5 stable (`subosito/flutter-action`) + parche oficial del dropdown |
| flutter_rust_bridge | 1.80.1 (workflow `bridge.yml`, compartido con Windows) |
| vcpkg | commit `9e593bb18ea69cc5095e012465dcd675a822ed0d` (ffmpeg, libvpx, aom, opus, libyuv…) |
| LLVM, create-dmg, pkg-config | Homebrew |
| NASM | 2.16.03, sitio oficial nasm.us |
| Features Rust | `flutter,hwcodec,unix-file-copy-paste` (+ `screencapturekit` en Apple Silicon) |

## Qué se cambió para macOS

Detalle archivo por archivo en `BUILD-macOS.md`. En resumen:

- **Reutilizado sin cambios** (código común con Windows): servidor `rustdesk.idevpy.com`
  y clave pública como valores predeterminados, respaldo en `hbb_common` (nunca cae a
  servidores públicos), idioma español, nombre visible "Soporte iDev" en la interfaz,
  logo de iDev, enlace al código fuente en "Acerca de".
- **Nuevo para macOS:**
  - `Soporte iDev.app`, identificador `com.idevpy.soporte`, nombre "Soporte iDev" en
    barra de menús, Dock, Finder y Ajustes del Sistema. Ejecutable interno `Soporte-iDev`.
  - Ícono `.icns` a partir del logo de iDev.
  - Barra de menús en español.
  - Licencias dentro de la app (`Contents/Resources/LICENSES`).
  - Firma ad-hoc completa y válida. La compilación oficial sin firmar deja el sello roto
    porque copia el helper `service` después de firmar.
- **Sin servicios persistentes:** como la carpeta se llama `Soporte iDev.app`, RustDesk no
  la considera "instalada" y no ofrece instalar el daemon/LaunchAgent ni actualizarse.
  El acceso remoto solo existe mientras la app está abierta.

## Validaciones automáticas (ambas arquitecturas)

| # | Verificación | Intel | Apple Silicon |
|---|---|---|---|
| 1 | Compilación exitosa | ✅ | ✅ |
| 2 | Existe el `.dmg`; `hdiutil verify` OK; contiene la app, el acceso a Aplicaciones y `LEAME.txt` | ✅ | ✅ |
| 3 | `.app` válida (estructura, `plutil -lint`, firma `codesign --verify --deep --strict`) | ✅ | ✅ |
| 4 | **Todos** los Mach-O del bundle tienen la arquitectura esperada; los binarios propios (`Soporte-iDev`, `service`, `liblibrustdesk.dylib`) son de una sola arquitectura | ✅ x86_64 | ✅ arm64 |
| 4b | `minos` más alto de todos los binarios = `LSMinimumSystemVersion` | ✅ 10.14 | ✅ 12.3 |
| 5 | `Info.plist`: `CFBundleName`/`DisplayName` "Soporte iDev", `com.idevpy.soporte`, ejecutable `Soporte-iDev`, esquema `soporte-idev` | ✅ | ✅ |
| 6 | `AppIcon.icns` idéntico al ícono de iDev del repositorio | ✅ | ✅ |
| 7 | La biblioteca contiene `rustdesk.idevpy.com` | ✅ | ✅ |
| 8 | Contiene la clave pública `O6qGUkD2…46G0=` | ✅ | ✅ |
| 9 | `rs-ny.rustdesk.com` y la clave pública oficial de RustDesk **ausentes en todo el bundle** | ✅ | ✅ |
| 10 | Runtime endurecido activo, sin desactivar la validación de bibliotecas | ✅ | ✅ |

## Prueba de lanzamiento en runner macOS

La app del `.dmg` se abrió con `open` en cada runner durante 40 s:

| Prueba | Intel | Apple Silicon |
|---|---|---|
| La app arranca y sigue viva a los 40 s | ✅ | ✅ |
| Captura: título "Soporte iDev", interfaz en español, logo iDev, ID, contraseña de un solo uso, estado **Listo**, aviso de permisos "Configurar" | ✅ | ✅ |
| Log: `start rendezvous mediator of rustdesk.idevpy.com` y registro en tu hbbs | ✅ | ✅ |
| Log: ningún host público de RustDesk | ✅ | ✅ |
| Sin contraseña permanente configurada | ✅ | ✅ |
| Ningún LaunchAgent/LaunchDaemon instalado | ✅ | ✅ |
| La orden "Salir" (mismo camino que Cmd+Q) termina la app y no queda proceso | ✅ | no ejecutada (la prueba se agregó en `09e5711`) |
| Barra de menús completamente en español | ✅ | parcial: Edit / View / Window / Help en inglés |

Nota: cada prueba registró un ID efímero en `rustdesk.idevpy.com`, igual que cualquier
cliente que se abre. No se modificó nada en el VPS.

## Pendiente: pruebas en una Mac real

Las pruebas interactivas **no se realizaron**: requieren una Mac física con alguien que
conceda los permisos de macOS. Que la app compile y arranque **no** demuestra que el
control remoto funcione. Hacer esta lista en una Mac Intel y en una Apple Silicon:

| # | Prueba | Cómo | Esperado |
|---|---|---|---|
| 1 | Descarga y apertura | Abrir el `.dmg`, arrastrar a Aplicaciones, abrir | Aviso de Gatekeeper; se autoriza en Ajustes → Privacidad y seguridad → "Abrir igualmente" |
| 2 | Estado Listo | Esperar unos segundos | Abajo dice "Listo" |
| 3 | ID y contraseña | Ver panel izquierdo | ID de 9 dígitos y contraseña de un solo uso |
| 4 | Permisos | "Configurar" en la tarjeta Permisos: Grabación de pantalla, Accesibilidad, Monitoreo de entrada | La app aparece en cada lista; tras activar y reabrir, la tarjeta desaparece |
| 5 | Conexión desde Windows | Desde Soporte iDev Windows, conectar al ID con la contraseña | Se conecta; la Mac muestra la ventana de conexión |
| 6 | Aceptación sin contraseña | Conectar sin contraseña | La Mac pide "Aceptar"; sin aceptar no hay acceso |
| 7 | Pantalla | Observar | Se ve la pantalla de la Mac (no solo el fondo) |
| 8 | Mouse y teclado | Mover, hacer clic, escribir en TextEdit | Funcionan; incluye tildes y ñ |
| 9 | Portapapeles | Copiar texto en cada lado y pegar en el otro | Pasa en ambos sentidos |
| 10 | Transferencia de archivos | Enviar un archivo a la Mac y otro desde la Mac | Llegan completos |
| 11 | Relay | Conectar desde otra red (p. ej. datos móviles) | Conecta; en la sesión figura relay |
| 12 | Fin de sesión | Desconectar desde la ventana de la Mac | El técnico pierde el acceso |
| 13 | Cierre | Cerrar con el botón rojo y luego Cmd+Q | Botón rojo solo oculta; tras Cmd+Q el ID aparece desconectado y no se puede conectar |
| 14 | Sin persistencia | Reiniciar la Mac | Soporte iDev no se abre solo |

## Limitaciones y observaciones

1. **Sin firma Developer ID ni notarización.** El aviso de Gatekeeper es esperado. Como
   la firma es ad-hoc, **cada versión nueva pide autorizar los permisos de nuevo**. El
   workflow ya está preparado para firmar y notarizar si se agregan los secretos (ver
   `BUILD-macOS.md`; esa parte no se probó).
2. **El botón rojo oculta la ventana, no cierra la app.** Es comportamiento de RustDesk:
   el acceso sigue disponible hasta salir con Cmd+Q o el menú. Está explicado en el `LEAME.txt`.
3. **API en puerto 21114.** La app intenta `http://rustdesk.idevpy.com:21114/api/heartbeat`
   y `/api/sysinfo` (funciones de RustDesk Pro). En OSS ese puerto está cerrado y falla
   sin efecto, igual que en Windows.
4. **STUN públicos para IPv6.** Al arrancar, RustDesk consulta servidores STUN de
   terceros (`stun.cloudflare.com`, `stun.l.google.com`, `stun.antisip.com`,
   `stun.nextcloud.com`) para averiguar la IPv6 pública. No son servidores de RustDesk
   ni transportan la sesión. Es código común con Windows y no se modificó; se puede
   desactivar si lo preferís.
5. **Nombres internos heredados.** La configuración queda en
   `~/Library/Preferences/com.carriez.Soporte-iDev/` (prefijo `ORG` de RustDesk). No se
   ve en la interfaz.
6. **Sin binario universal.** Las dos arquitecturas tienen mínimos distintos (10.14
   frente a 12.3, por ScreenCaptureKit); se priorizaron dos paquetes.
7. **GitHub Actions bloqueado (23/10/2026).** Desde el 22–23/10 GitHub rechaza toda
   ejecución nueva en el repo con "Actions has been disabled for this repository",
   aunque la configuración del repo indica Actions habilitado, la facturación no muestra
   consumo relevante y el workflow macOS aparecía desactivado sin que nadie lo hiciera.
   Afecta también al workflow de Windows. Requiere revisión desde la web de GitHub o con
   el soporte de GitHub.
8. **macOS mínimo.** Es el que declaran y exigen los binarios; no se probó en esas
   versiones antiguas, solo en los runners (macOS 15 Intel y macOS 14 Apple Silicon).

## Contenido de `dist/` (macOS)

```
Soporte-iDev-macOS-Intel.dmg          instalador Intel
Soporte-iDev-macOS-AppleSilicon.dmg   instalador Apple Silicon
SHA256SUMS.txt                        hashes (Windows y macOS)
README-macOS.txt                      instrucciones para clientes (= LEAME.txt del .dmg)
BUILD-macOS.md                        cómo recompilar y qué se cambió
INFORME-macOS.md                      este informe
```
