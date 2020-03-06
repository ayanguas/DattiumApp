# Injestacion en la BBDD

En esta sección se encuentra el script *local_db_creation.py*, en el script se leen las 10000 primeras filas del archivo *MiningProcess_Flotation_Plant_Database.csv*. Se formatea el nombre de las columnas para que no tenga carácteres confilictivos como el '%'. Finalmente, se crea la conexión a la BBDD PostgreSQL i se cargan los datos. 
