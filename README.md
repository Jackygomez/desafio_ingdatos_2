# Proyecto Desafio Ingedatos 2 - SQL Server

Este proyecto consta de dos microservicios que interactúan con una base de datos SQL Server:

1. **Microservicio 1**: Recibe un archivo CSV y almacena coordenadas en SQL Server.
2. **Microservicio 2**: Procesa las coordenadas y obtiene códigos postales usando la API `postcodes.io`.

## Configuración

1. Instala Docker y Docker Compose.
2. Configura SQL Server y crea una base de datos llamada `employeedirectorydb`.
3. Asegúrate de tener credenciales para conectarte a SQL Server.

## Ejecución

1. Clona el repositorio y navega al directorio del proyecto.
2. Asegúrate de tener un archivo `.env` con las credenciales correctas:
   ```txt
   SQL_SERVER='employeedirectorydb1.database.windows.net'
