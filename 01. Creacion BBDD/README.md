# Injestacion en la BBDD

1. **local_db_creation.py**, en eeste script se carga el archivo *MiningProcess_Flotation_Plant_Database.csv*. Se formatea el nombre de las columnas para que no tenga carácteres confilictivos como el '%'. Finalmente, se crea la conexión a la BBDD PostgreSQL i se cargan los datos. 

2. **extract_transform_load.py**, en este script se cargan los datos de la BBDD *DattiumApp*, se hace la media por horas de las señales y finalmente en la BBDD *DattiumApp* del servidor 192.168.1.33
