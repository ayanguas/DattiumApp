# DattiumApp
Aplicación de visualización en la nube de Dattium

## Dependencias
1. [*PostgreSQL*](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. Dataset *Quality Prediction in a Mining Process* se encuentra en un .zip en la carpeta *data*

## Instrucciones

1. Descomprimir el archivo *MiningProcess_Flotation_Plant_Database.csv.zip*
2. Instalar [*PostgreSQL*](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) version 12.
3. Abrir PgAdmin, programa para la gestión de los servidores y BBDD *PostgreSQL.
4. Crear la BBDD en el servidor PostgreSQL 12
    1. Click derecho sobre PostgreSQL 12 y seleccionamos crear una nueva BBDD con el nombre **DattiumApp**
    2. Click derecho sobre la PostgreSQL 12 y seleccionamos crear un nuevo Login/Role Group con nombre de usuario **test** y password **test123** (se cambia en la pestaña *Definition*), finalmente, le habilitamos todos los permisos, en la pestaña *privileges*, habilitaremos las opciones *Can login?* y *Superuser*

## I. Creación de la BBDD PostgreSQL

Para la creación de la BBDD será necesario instalar [*PostgreSQL*](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) al PC que se vaya a utilizar para el proyecto. Es recomendable utilizar **pgAdmin** para la gestión de los servidores y BBDD *PostgreSQL* (En la propia instalación de PostgreSQL con el link de descarga, ya viene la instalación de pgAdmin).

Si se quiere trabajar en **local**, se debe abrir el programa pgAdmin, entrar dentro del servidor PostgreSQL 12, creado por defecto, y crear una nueva BBDD. Para conectarse a un **servidor** remoto, crearemos un nuevo servidor en pgAdmin, para la configuración:
  1. En el apartado **general**, le damos un nombre al servidor
  2. En el apartado **connection**, en *Host name/adress* añadiremos la IP del servidor y cambiaremos el *Username* y *Password* por el indicado

## II. Configuración de PostgreSQL para acceso remoto

Por defecto PostgreSQL está configurado para trabajar solo en local, para poder habilitar el acceso remoto se debe configurar de la siguiente manera:
  1. Se debe modificar el archivo *postgresql.conf* y modificar la linea *listen_addres = 'localhost'* por **listen_addres = '*'**
  2. Se debe modificar el archivo *pg_hba.conf* se debe añadir la siguiente linea *host all all 0.0.0.0/0 md5*
  
  
[Reference](https://blog.bigbinary.com/2016/01/23/configure-postgresql-to-allow-remote-connection.html)

## III. Creación de la BBDD y preparación de los datos

Antes de ejecutar los scripts se debe descomprimir el archivo ***MiningProcess_Flotation_Plant_Database.csv.zip*** que se encuentra en la carpeta **data**. En la carpeta **01. Creacion BBDD** encontraremos dos scripts. En primer lugar se debe ejecutar ***01_local_db_creation.py***, este nos creara una BBDD con el raw data del data set utilizado. En segundo lugar, se debe ejecutar ***02_extract_transform_load.py***, este nos creara una segunda BBDD con los datos ya transformados y preparados para el uso de la aplicación.

## IV. Ejecución de la APP

Una vez ya se tiene instalado PostgreSQL y cargado los datos a la BBDD. Ya se puede ejecutar el script ***app.py***, que se encuentra en la carpeta **03. App**, una vez ejecutado el script, se debe abrir el navegador y entrar a la siguiente direccion http://127.0.0.1:8050/, dónde se estará ejecutando la aplicación.
