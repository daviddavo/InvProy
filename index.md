---
Title: InvProy
---
# InvProy #

Proyecto de Investigación de Bachillerato de Excelencia. Desde 2015.

Por favor, documentad bugs e incidencias en issues.

## Sobre el programa ##

### ¿Qué es un simulador de redes? ###
Antes de probar las cosas en el mundo real, podemos hacer una simulación. Usamos un simulador para probar las cosas y comprobar como funcionan. En el ámbito educativo (no profesional), sirven para aprender con pocos recursos: en lugar de comprar 50 ordenadores y 200 metros de cables, podemos usar un simulador para enseñar sobre un tema.
Una red es una conexión entre dispositivos.

Si tenemos en cuenta ambas cosas, un simulador de redes no es más que un programa educativo para aprender sobre el funcionamiento de estas.

### Capturas de pantalla ###
> Las capturas de pantalla son de InvProy α, el "prototipo"
> La interfaz será cambiada del motor Gtk+ a Qt

![](http://invproy.ddavo.me/screenshots/2016-09-12-230644_1000x700_scrot.png)
<center> Captura de pantalla del programa </center>

### Funcionalidades ###
* Crear dispositivos, modificar sus propiedades (IP, MAC y Nombre)
* Conectar dispositivos mediante cables
* Ordenador, Switch y Hub
* Enviar Ping's entre dispositivos

### Uso del programa ###
> Recomendable esperarse a la fase Beta

1. Descargar el programa
2. Instalarlo al ejecutar setup.py
3. Usar

### Dependencias: ###
* python3-gobject
* python3
* pycairo

### Tecnologías usadas ###

* Python 3 (Última versión)
* Toda la suite de Gtk+
* Jekyll (GitHub pages) para la página web
* Travis (Autotest builds)
* Codacy (Para encontrar errores programáticos)

## Sobre el proyecto ##

El proyecto comenzó con la mera idea de construir algo, de hacer algo y así aprender a programar. Mi tutor de proyecto me recomendó hacer algo que se pudiese usar después de un par de años en clase: Un simuldor de redes.

Una vez acabada la primera versión, con muchos fallos de principiante, dará comienzo el desarrollo de la nueva versión, InvProy β, que debería funcionar completamente en Linux y Windows, y Android si es posible.

### No sólo un simulador de redes ###

La idea principal no es crear el programa, sino que el programa sirva para otros. No tan sólo para el uso didáctico en las clases, también para aprender a programar. Al ser software libre, cualquier alumno podría ver el código o colaborar en el proyecto. Para ello necesitamos una buena documentación y una buena cobertura.

### ¿Por qué se está tardando en empezar el desarrollo de la fase Beta ? ###

El desarrollador principal es un estudiante de SEGUNDO de BACHILLERATO. Además, hay bastantes cambios importantes que requieren de bastante tiempo para diseñar, pero también para aprender (e.g: Se cambiará la interfaz de Gtk+ a Qt, pero para ello es necesario aprender sobre Qt).

También la parte de la cobertura: crear un board en Trello, una página web con Jekyll, dar formato a los documentos, traducir páginas al inglés y redactar readmes... Son todo pequeñas tareas que en suma son muchas horas.

### Memorias del proyecto ###

| Fecha   | Título                                               | Presentado en... | Comentario | Enlace |
|---------|---------|---------|---------|---------|
| Oct2016 | Invproy α: Un simulador de redes por y para alumnos  | Proyecto de Investigación bachillerato de Excelencia | Primera versión. 50 páginas máximo + anexos | [GitHub](https://github.com/daviddavo/InvProy-tex/raw/master/InvProy.pdf) |
| Jan2017 | Invproy α.zip: Un simulador de redes por y para alumnos | [II Encuentro Preuniversitario de Jóvenes Investigadores UCM](https://www.ucm.es/jovenesinvestigadores) | Máximo 10 folios | [GitHub](https://github.com/daviddavo/InvProy-tex/raw/EPCJI/InvProy.pdf) |

## Contacto ##

Actualmente sólo hay una persona trabajando en el proyecto.

* David Davó Laviña (Founder) <[david@ddavo.me](david@ddavo.me)>