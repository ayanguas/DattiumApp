# DattiumApp
Aplicación de visualización en la nube de Dattium



## Creación de la BBDD PostgreSQL

Para la creación de la BBDD será necesario instalar *PostgreSQL* al PC que se vaya a utilizar para el proyecto. Es recomendable utilizar [**pgAdmin**](https://www.pgadmin.org/download/) para la gestión de los servidores y BBDD *PostgreSQL*.

Si se quiere trabajar en **local**, se debe abrir el programa pgAdmin, entrar dentro del servidor PostgreSQL 12, creado por defecto, y crear una nueva BBDD. Para conectarse a un **servidor** remoto, crearemos un nuevo servidor en pgAdmin, para la configuración:
  1. Le damos un nombre al servidor
  2. En el apartado **connection**, en *Host name/adress* añadiremos la IP del servidor y cambiaremos el *Username* y *Password*

## Configuración de PostgreSQL para acceso remoto

Por defecto PostgreSQL está configurado para trabajar solo en local, para poder habilitar el acceso remoto se debe configurar de la siguiente manera:
  1. Se debe modificar el archivo *postgresql.conf* y modificar la linea *listen_addres = 'localhost'* por **listen_addres = '*'**
  2. Se debe modificar el archivo *pg_hba.conf* se debe añadir la siguiente linea *host all all 0.0.0.0/0 md5*
[Link](https://blog.bigbinary.com/2016/01/23/configure-postgresql-to-allow-remote-connection.html)
