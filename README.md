# DattiumApp
Aplicación de visualización en la nube de Dattium

## Dependencias
1. [*PostgreSQL*](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. Dataset *Quality Prediction in a Mining Process* se encuentra en un .zip en la carpeta *data*

## Instrucciones

1. Abrir el terminal de conda, utilizando el commando *cd* nos posicionaremos en la carpeta del proyecto y ejecutaremos el siguiente comando: *conda env create -f dependencies/DattiumApp.yml*
2. Activamos el environment: *conda activate DattiumApp* 
3. Descomprimir el archivo *MiningProcess_Flotation_Plant_Database.csv.zip*
4. Instalar [*PostgreSQL*](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) version 12.
5. [**Opcional para conexión en remoto**] Configuración de *PostgreSQL* [[1]](https://blog.bigbinary.com/2016/01/23/configure-postgresql-to-allow-remote-connection.html)
    1. Abrimos con un editor de texto el archivo *PostgreSQL/12/data/postgresql.conf* y modificar la linea *listen_addres = 'localhost'* por **listen_addres = '*'**
    2. Abrimos con un editor de texto el archivo *~/PostgreSQL/12/data/pg_hba.conf* y se añade la siguiente linea *host all all 0.0.0.0/0 md5* justo despues de la linea *host all all 127.0.0.1/32 md5*. En windows la carpeta PostgreSQL se encuentra en *C:/Archivos de programa/PostgreSQL*.
6. Abrir PgAdmin, programa para la gestión de los servidores y BBDD *PostgreSQL*.
7. Crear la BBDD en el servidor PostgreSQL 12
    1. Click derecho sobre PostgreSQL 12 y seleccionamos crear una nueva BBDD con el nombre **DattiumApp**
    2. Click derecho sobre la PostgreSQL 12 y seleccionamos crear un nuevo Login/Role Group con nombre de usuario **test** y password **test123** (se cambia en la pestaña *Definition*), finalmente, le habilitamos todos los permisos, en la pestaña *privileges*, habilitaremos las opciones *Can login?* y *Superuser*
8. Ejecutamos el script **01. Creacion BBDD/01_local_db_creation.py**, nos creara una tabla, llamada *raw*, con el raw data en la BBDD *DattiumApp*
9. Ejecutamos el script **01. Creacion BBDD/02_extract_transform_load.py**, extrae el raw data, lo transforma para la aplicación y lo guarda en otra tabla, llamada *signals*, de la BBDD.
10. Ejecutamos el script **03. App/app.py**
11. Accedemos al browser a: http://127.0.0.1:8050/


Una vez realizado los pasos 1-7, cada vez que se quiera abrir la aplicación simplemente repitiendo los pasos 10 y 11 será suficiente, siempre que tengamos el environment DattiumApp activado paso 2.
