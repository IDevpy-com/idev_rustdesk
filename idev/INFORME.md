# Informe: Soporte iDev para Windows x64

Fecha: 21/10/2026

## Resultado

El ejecutable `Soporte-iDev.exe` se compiló y funciona. Es un único archivo de 25,9 MB, no requiere instalación y no está firmado.

Ubicación: `C:\proyectos\rustdesk\dist\Soporte-iDev.exe`

```
SHA-256  57a92c650e40fae74b032617999506ab1d735d477bd02937ae8fac2c5a4e7920  Soporte-iDev.exe
SHA-256  7220d70b9467cfc396cbba7cc9318362058b30b9574fcd6df5a6d3ccadd5d7c7  Soporte-iDev-1.5.0-portable-carpeta.zip
```

El `.exe` es un autoextraíble, el empaquetador portable oficial de RustDesk. Al abrirlo descomprime la app en `%LOCALAPPDATA%\soporte-idev` y la ejecuta.

El zip trae la misma app como carpeta. Sirve para diagnóstico o para usarla sin el autoextraíble.

## Versión de RustDesk utilizada

- RustDesk OSS **1.5.0**, el último release estable al 30/09/2026.
  - Tag `1.5.0`, commit `fada664df7a294d1d1a9ca3e7cd3637069122f17`.
  - Submódulo `libs/hbb_common` en `229b904508364c8997aad0fb5af57effac859f60`.
- Código modificado: <https://github.com/edbenrio/rustdesk/tree/soporte-idev>, commit `6e77a2b`. Es un fork público, como exige la AGPL.
- Build: GitHub Actions, run <https://github.com/edbenrio/rustdesk/actions/runs/39537364207>.

## Por qué se compiló en GitHub Actions

Esta PC tiene un solo disco, con 17,7 GB libres. Tampoco tenía instalados Rust, VS Build Tools, LLVM, CMake ni vcpkg. Una compilación fiel al workflow oficial necesita unos 30 GB.

Por eso se usó la alternativa gratuita que elegiste: los runners Windows de GitHub. El workflow replica el job oficial `build-for-windows-flutter` con las mismas versiones:

- Flutter 3.24.5 con el motor de rustdesk/engine y el parche oficial del dropdown.
- Rust 1.75.
- LLVM 15.0.6.
- vcpkg en `9e593bb1`.
- Features `--hwcodec --vram`.

**Dependencias instaladas en esta PC:** solo Pillow, en un entorno virtual temporal, para generar los íconos. No se instaló nada más en el sistema.

## Cambios realizados

- **Servidor integrado:** sin `custom.txt` (requiere firma de RustDesk Pro) y sin depender del nombre del `.exe`.
  - Valores predeterminados: ID `rustdesk.idevpy.com`, Relay vacío, API vacío y Key `O6qGUkD2hlCk26erLMuMmBk3+PReg03kaXMebv+46G0=`.
  - Se ven y se pueden editar en Ajustes → Red.
  - Las constantes de respaldo de `hbb_common` también apuntan a tu servidor. Si alguien borra el campo, el cliente nunca cae a `rs-ny.rustdesk.com`.
  - Solo se incluye la clave pública. La clave privada no se usa ni se incluye.
- **Nombre:**
  - Visible: "Soporte iDev" (ventanas, textos, bandeja, "Acerca de", metadatos del `.exe`).
  - Interno: "Soporte-iDev". RustDesk exige `[a-zA-Z0-9-]+` para servicio, registro e instalación.
- **Íconos y logo:** se usó el logo de idevpy.com, extraído del favicon del sitio en 1523×391 px.
  - Ícono `.ico` multi-tamaño: símbolo `</>` azul sobre fondo blanco redondeado.
  - Logo claro y oscuro en la pantalla principal.
  - Texto "Cargando..." en el extractor.
- **Idioma:** español por defecto.
- **Licencia y atribución:**
  - Se conservan el copyright de Purslane Tech y el texto "Con tecnología de RustDesk".
  - Se agregó el enlace al código fuente en "Acerca de".
  - El paquete incluye `LICENSES/`.
- **Seguridad:** no se modificó ningún mecanismo de seguridad, consentimiento ni contraseña. No se agregó telemetría.

El detalle archivo por archivo está en `BUILD.md`, y los parches en `source/`.

## Resultado de la compilación

| Intento | Resultado | Causa / corrección |
|---|---|---|
| 1 | Falló en vcpkg | `aomedia.googlesource.com` respondió HTTP 503, una caída externa temporal. Se reintentó. |
| 2 | Compiló; falló la verificación | El verificador buscaba la cadena `Soporte-iDev`, que el compilador emite partida. Se ajustó para buscar `Soporte-`. El servidor y la clave sí estaban, y el servidor público no. |
| 3 | Falló el empaquetado | Error de mi script: `ls` con `pipefail`. Se corrigió. |
| 4 | **Éxito** | Run 39537364207 |

## Pruebas ejecutadas en esta PC (Windows 11 IoT Enterprise LTSC 2024, build 26100, x64)

| Prueba | Resultado |
|---|---|
| El `.exe` se inicia (doble clic, sin instalar) | ✅ |
| Nombre visible "Soporte iDev" (título, textos, "Acerca de", metadatos) | ✅ |
| Ícono personalizado (barra de título, barra de tareas, `.exe`) | ✅ |
| Interfaz en español | ✅ |
| Ajustes → Red: ID `rustdesk.idevpy.com`, Relay vacío, API vacío, Key correcta | ✅ (captura) |
| La DLL contiene tu servidor y clave, y no `rs-ny.rustdesk.com` ni la clave pública oficial | ✅ (verificación automática en CI) |
| Se muestra el ID (`25 909 620`) y la contraseña temporal | ✅ |
| La contraseña temporal cambia en cada ejecución | ✅ (`n5y7et` → `rq4iau` → …) |
| Estado "Listo" y registro en tu hbbs (`key_confirmed = true`) | ✅ |
| Única conexión de red: TCP `186.123.3.68:21116`, sin servidores públicos | ✅ |
| Puertos del servidor: 21115–21119 abiertos, 21114 (API Pro) cerrado | ✅ (esperado en OSS) |
| Sin servicio, autoarranque, tareas programadas ni Program Files | ✅ |
| Sin contraseña permanente; modo "aceptar con contraseña o clic" | ✅ |
| Permisos predeterminados (teclado/ratón, portapapeles, archivos) habilitados | ✅ |
| Arranques repetidos (8 en total, 3 con datos limpios) | ⚠️ 7/8 correctos (ver limitaciones) |

## Prueba de uso real

El 21/10/2026 el usuario hizo pruebas reales entre dos computadoras y reportó que
**todo funciona correctamente**:

| Prueba (realizada por el usuario) | Resultado |
|---|---|
| Conexión desde otra PC al ID del cliente con la contraseña temporal | ✅ |
| Aparece la ventana de aceptación de la conexión | ✅ |
| Visualización de la pantalla | ✅ |
| Control de teclado y ratón | ✅ |
| Portapapeles | ✅ |
| Transferencia de archivos | ✅ |
| Conexión a través del relay hbbr (otra red / NAT) | ✅ |

No quedan pruebas funcionales pendientes.

## Limitaciones y observaciones

1. **No está firmado digitalmente.** SmartScreen va a mostrar "Windows protegió su PC". El cliente debe elegir "Más información → Ejecutar de todas formas". Para evitarlo hace falta un certificado de firma de código (ver `BUILD.md`).
2. **Ventana en blanco una vez.** En la primerísima ejecución en esta PC la ventana quedó en blanco. No se reprodujo en los 7 arranques siguientes, incluidos dos con datos limpios. Cerrar y volver a abrir lo soluciona; está indicado en el `README.txt`. La causa no está confirmada; podría ser la inicialización del motor gráfico de Flutter en un equipo con GPU híbrida Intel/NVIDIA.
3. **Botón "Instalar".** La pantalla principal muestra la tarjeta estándar de RustDesk que sugiere instalar para un mejor funcionamiento con UAC. Instalar requiere que el cliente haga clic y acepte UAC, y no se hace automáticamente.
4. **Pantallas elevadas.** Sin instalar, el técnico no puede controlar ventanas que piden elevación (UAC) del cliente. Es el comportamiento normal de RustDesk portable.
5. **Solo x64.** No se generó versión ARM64 ni MSI.
6. **Distribución.** Está publicado como pre-release en
   <https://github.com/edbenrio/rustdesk/releases/tag/soporte-idev-1.5.0>.
   Descarga directa: <https://github.com/edbenrio/rustdesk/releases/download/soporte-idev-1.5.0/Soporte-iDev.exe>.

## Contenido de `dist/`

```
Soporte-iDev.exe                           ejecutable único para clientes
Soporte-iDev-1.5.0-portable-carpeta.zip    misma app en carpeta (alternativa / diagnóstico)
SHA256SUMS.txt                             hashes
README.txt                                 instrucciones para clientes
BUILD.md                                   cómo recompilar y qué se cambió
INFORME.md                                 este informe
LICENSES/                                  AGPL-3.0 de RustDesk y NOTICE de atribución
source/                                    parches (git format-patch), parche de hbb_common, script local
```
