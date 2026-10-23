Soporte iDev para macOS
=======================

Soporte iDev permite que un técnico de iDev vea y controle su Mac para
ayudarle, solo mientras usted tenga la aplicación abierta y le haya dado su
ID y su contraseña temporal.

Qué archivo descargar
---------------------
  Mac con procesador Intel ........ Soporte-iDev-macOS-Intel.dmg (macOS 10.14 o posterior)
  Mac con Apple M1, M2, M3, M4... . Soporte-iDev-macOS-AppleSilicon.dmg (macOS 12.3 o posterior)

Para saber cuál tiene: menú Apple () > Acerca de esta Mac. Si dice "Chip
Apple M...", es Apple Silicon; si dice "Procesador ... Intel", es Intel.

1. Instalar
-----------
  1. Abra el archivo .dmg descargado.
  2. Arrastre "Soporte iDev" a la carpeta "Applications" (Aplicaciones).
     También puede abrirla directamente desde el .dmg, sin instalar.
  3. Expulse el disco "Soporte iDev" en el Finder.

2. Primera apertura
-------------------
Esta versión todavía no está firmada con un certificado de Apple, por eso
macOS muestra un aviso la primera vez. Es el mecanismo normal de macOS para
aplicaciones de desarrolladores no registrados; no hace falta desactivar
ninguna protección del sistema.

  macOS 15 (Sequoia) o posterior:
    1. Abra "Soporte iDev". macOS avisa que no pudo verificarla:
       pulse "Listo" (NO pulse "Trasladar a la Papelera").
    2. Abra Ajustes del Sistema > Privacidad y seguridad.
    3. Baje hasta "Seguridad": junto al aviso sobre "Soporte iDev" pulse
       "Abrir igualmente" (o "Abrir de todos modos") y confirme con su
       contraseña o Touch ID.
    4. Vuelva a abrir Soporte iDev y pulse "Abrir".

  macOS 14 (Sonoma) o anterior:
    1. En Aplicaciones, haga clic derecho (o Control + clic) sobre
       "Soporte iDev" > Abrir.
    2. En el aviso, pulse "Abrir".

Esto se hace una sola vez por cada versión descargada.

3. Permisos de macOS
--------------------
Para que el técnico pueda ver la pantalla y usar el teclado y el mouse,
macOS pide autorizar a Soporte iDev. La ventana principal muestra un aviso
"Permisos" con el botón "Configurar" para cada uno:

  - Grabación de pantalla (o "Grabación de pantalla y audio del sistema"):
      sin este permiso el técnico solo ve el fondo de escritorio.
  - Accesibilidad: necesario para controlar el mouse y el teclado.
  - Monitoreo de entrada: necesario para el teclado.

Para cada uno: pulse "Configurar", y en Ajustes del Sistema > Privacidad y
seguridad > (permiso) active el interruptor de "Soporte iDev". Si macOS lo
pide, cierre y vuelva a abrir Soporte iDev.

Si "Soporte iDev" no aparece en la lista, pulse "+", elija
Aplicaciones > Soporte iDev y actívelo.

Puede quitar estos permisos cuando quiera desde el mismo lugar.

4. Recibir asistencia
---------------------
  1. Abra Soporte iDev y espere a que abajo diga "Listo".
  2. Dígale al técnico de iDev su "ID" y su "Contraseña" (temporal).
  3. Si el técnico usa la contraseña, la conexión se acepta; si no, usted
     debe pulsar "Aceptar" en la ventana que aparece. En ambos casos esa
     ventana muestra la conexión activa y permite desconectarla en
     cualquier momento.

No se configura ninguna contraseña permanente ni acceso desatendido.
Soporte iDev no se inicia solo con la Mac y no instala servicios en
segundo plano.

5. Terminar
-----------
El botón rojo de la ventana solo la OCULTA: Soporte iDev sigue abierto y
se puede seguir conectando. Para terminar de verdad use el menú
"Soporte iDev" > "Salir de Soporte iDev", o Cmd + Q, o clic derecho sobre
su ícono en el Dock > Salir.
Mientras la aplicación esté cerrada, nadie puede conectarse a su Mac.

Para desinstalar, arrastre "Soporte iDev" desde Aplicaciones a la Papelera.

Información
-----------
Servidor: rustdesk.idevpy.com (servidor privado de iDev)
Soporte iDev está basado en RustDesk (https://rustdesk.com), licencia
AGPL-3.0. Código fuente: https://github.com/IDevpy-com/idev_rustdesk/tree/soporte-idev
Los avisos de licencia están dentro de la aplicación, en
Contents/Resources/LICENSES.
iDev - https://idevpy.com
