# DattiumApp
Aplicación de visualización en la nube de Dattium

## Dependencias
1. [*PostgreSQL*](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads)
2. Dataset *Quality Prediction in a Mining Process* se encuentra en un .zip en la carpeta *data*

## Instrucciones

#### PostgreSQL
1. Instalar [*PostgreSQL*](https://www.enterprisedb.com/downloads/postgres-postgresql-downloads) version 12.
![Download PostgreSQL](https://github.com/ayanguas/DattiumApp/blob/master/img/1_download_psql.png?raw=true "Download PostgreSQL")
2. [**Opcional**] Para la conexión en remoto: Configuración de *PostgreSQL* [[1]](https://blog.bigbinary.com/2016/01/23/configure-postgresql-to-allow-remote-connection.html)
    1. Abrimos con un editor de texto el archivo *PostgreSQL/12/data/postgresql.conf* y modificar la linea *listen_addres = 'localhost'* por **listen_addres = '*'**
    2. Abrimos con un editor de texto el archivo *~/PostgreSQL/12/data/pg_hba.conf* y se añade la siguiente linea *host all all 0.0.0.0/0 md5* justo despues de la linea *host all all 127.0.0.1/32 md5*. En windows la carpeta PostgreSQL se encuentra en *C:/Archivos de programa/PostgreSQL*.
3. Abrir PgAdmin, programa para la gestión de los servidores y BBDD *PostgreSQL*.
4. Crear la BBDD en el servidor PostgreSQL 12
    1. Click derecho sobre PostgreSQL 12 y seleccionamos crear una nueva BBDD con el nombre **DattiumApp**
    ![Create DB](https://github.com/ayanguas/DattiumApp/blob/master/img/2_create_db.png?raw=true "Create DB")
    ![Name DB](https://github.com/ayanguas/DattiumApp/blob/master/img/3_name_db.png?raw=true "Name DB")
    2. Click derecho sobre la PostgreSQL 12 y seleccionamos crear un nuevo Login/Role Group con nombre de usuario **test** y password **test123** (se cambia en la pestaña *Definition*), finalmente, le habilitamos todos los permisos, en la pestaña *privileges*, habilitaremos las opciones *Can login?* y *Superuser*
    ![Create User](https://github.com/ayanguas/DattiumApp/blob/master/img/4_create_user.png=100x100 "Create User")
    ![Name User](https://github.com/ayanguas/DattiumApp/blob/master/img/5_name_user.png "Name User")
    ![Password User](https://github.com/ayanguas/DattiumApp/blob/master/img/6_pswrd_user.png "Password User")
    ![Privilege User](https://github.com/ayanguas/DattiumApp/blob/master/img/7_privilages_user.png "Privilege User")
#### Environment
5. Abrir el terminal de conda, utilizando el commando *cd* nos posicionaremos en la carpeta del proyecto y ejecutaremos el siguiente comando *conda env create -f dependencies/DattiumApp.yml*. Ejemplo en terminal:
    - *cd C:\Git\DattiumApp*
    - *conda env create -f dependencies/DattiumApp.yml*
6. Activamos el environment: *conda activate DattiumApp* 
#### Datos
7. Descomprimir el archivo *MiningProcess_Flotation_Plant_Database.csv.zip*
8. Ejecutamos el script **01. Creacion BBDD/01_local_db_creation.py**, nos creara una tabla, llamada *raw*, con el raw data en la BBDD *DattiumApp*
9. Ejecutamos el script **01. Creacion BBDD/02_extract_transform_load.py**, extrae el raw data, lo transforma para la aplicación y lo guarda en otra tabla, llamada *signals*, de la BBDD.
#### App
10. Ejecutamos el script **03. App/app.py**
11. Accedemos al browser a: http://127.0.0.1:8050/


Una vez realizado los pasos 1-7, cada vez que se quiera abrir la aplicación simplemente repitiendo los pasos 10 y 11 será suficiente, siempre que tengamos el environment DattiumApp activado paso 2.
