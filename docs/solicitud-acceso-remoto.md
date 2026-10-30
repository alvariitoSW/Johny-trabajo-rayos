# Borrador · petición de acceso remoto a Informática

Rellena lo que va entre corchetes. No pongas datos de pacientes en el correo.

---

**Asunto:** Solicitud de acceso remoto a un PC del hospital para un estudio de investigación

Buenos días:

Soy [nombre], [cargo y servicio]. Estoy preparando un estudio observacional retrospectivo de radiómica sobre TC de
metástasis hepáticas de origen colorrectal («[título del estudio]»), [pendiente de / aprobado por] el Comité de Ética
de la Investigación [con el código ____].

El procesamiento de las imágenes se hará **solo en un PC del hospital** ([nombre o inventario del equipo, servicio,
ubicación]), con datos codificados, como exige el protocolo y el RGPD. En ese PC funcionará una aplicación local que no
se conecta a internet ni abre puertos a la red: solo se puede usar desde el propio equipo.

Os pido:
1. **Acceso remoto a ese PC** (VPN y escritorio remoto, o la solución que uséis, p. ej. Citrix), también desde
   [móvil o tableta, y si es del hospital o personal], para poder trabajar sin estar delante del equipo.
2. Permiso para instalar, en mi usuario y sin permisos de administrador, **Python 3.11** y un entorno virtual con las
   librerías del estudio (se instalan desde PyPI; la lista con versiones fijadas está en `requirements.txt`).
3. Si es posible, una **carpeta de trabajo** en ese PC (o en una unidad de red del hospital) con copia de seguridad y
   acceso solo para el equipo investigador.

Si hace falta, os paso el protocolo y la lista de software. Quedo a vuestra disposición para cualquier requisito de
seguridad.

Un saludo,
[nombre] · [teléfono o extensión]

---

**Antes de enviarlo:** si el acceso será desde tu móvil personal, pregunta también al **delegado de protección de
datos** si está permitido ver datos codificados de pacientes en ese dispositivo a través del escritorio remoto.
