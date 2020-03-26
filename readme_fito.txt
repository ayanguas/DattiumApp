Dependencias
1.- Datos - Quality Prediction... pero ya esta en el Git no pongas el link.

1.- PostgresSQL (Ya tiene pgAdmin) - Local y Remoto
2.- pgAdmin - Remoto 

1.- Librerias (?)
2.- Virtual Enviroment
3.- 


Instrucciones
1.- Quitar del zip el .csv
2.- Instalar Postgress SQL (version 12 windows/mac)
3.- Abrir pgAdmin 
4.- Crear una BBDD en el Server SQL 12  
	4.1.- Click derecho en el server /bbdd actual y crear una nueva con el nombre DattiumApp
	4.2.- Crear un usuario con nombre test password test123,
	4.3.- Darle permiso absoluto maestro y todo
5.- Ejecutar el 01_local_db_creation.py
6.- Ejecutar el 02_extract_transform_load.py

7.- Ejecutar 03. App

8.- Acceder en el browser a : http://127.0.0.1:8050/

