FROM python:3.9

# Instalar dependencias para ODBC y el controlador ODBC para SQL Server
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev \
    && apt-get install -y curl gnupg \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list -o /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 mssql-tools18 \
    && apt-get clean

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt  # Instalar dependencias de Python

EXPOSE 5002
CMD ["python", "app.py"]
