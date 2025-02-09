# Análisis de Datos Tomados de API Open-Meteor
## Requisitos
- Obtener de la API de Open-Meteor la información de parámetros diarios: `"daily": ["temperature_2m_max", "temperature_2m_min", "temperature_2m_mean", "rain_sum", "precipitation_hours", "wind_speed_10m_max", "shortwave_radiation_sum"]`
- Escoger un rango de fechas (de preferencia, dos años o más)
- Revisar que no existan campos duplicados, nulos.
- Escoger variable objetivo (lluvia, radiación, viento o temperatura)
- Hacer un análisis exploratorio (histogramas, gráficos de caja, matriz de correlación)
- Escalado de datos (MinMax, Standard)
- Implementar un algoritmo de aprendizaje (RandomForest u otro)
- Imprimir métricas resultantes de desempeño

##  Obtener de la API de Open-Meteor la información de parámetros diarios
### Servicio de AWS
Para la Extracción de datos desde la API Open-Meteor, se usó el servicio Lambda de AWS.

Fechas seleccionadas para la obtención de datos:
- Enero del 01 al 31
- Marzo del 01 al 31
- Mayo del 01 al 31
- Julio  del 01 al 31
- Agosto del 01 al 31
- Octubre del 01 al 31
- Diciembre del 01 al 31
#### Archivos descargados de S3
```
https://github.com/CirceDelLop/ClimaAcademiaDataEngineer/blob/main/ejercicio/archivoscsv/datosClimaticos_2025-02-09.csv
```
```
https://github.com/CirceDelLop/ClimaAcademiaDataEngineer/blob/main/ejercicio/archivoscsv/run-1739065936191-part-r-00000.csv
```

#### Código en función Lambda
```
import json
import requests
import pandas as pd
import boto3
import os
from datetime import datetime

def lambda_handler(evento, contexto):
    # Parámetros de la API (ubicación: Los Reyes Culhuacán)
    latitude = 19.3453263
    longitude = -99.1098627
    timeZone = "America/Mexico_City"

    # Período: Enero de 2023 a Enero 2025
    years = [2020,2021,2022,2023, 2024]
    months = ["01","03","05","07","08","10","12"]

    # Lista de parámetros a solicitar
    daily_params = "temperature_2m_max,temperature_2m_min,temperature_2m_mean,rain_sum,precipitation_hours,wind_speed_10m_max,shortwave_radiation_sum"

    # Lista para almacenar DataFrames
    dataframes = []

    for year in years:
        for month in months:    
            # Solicitud a la API de Open-Meteo para obtener los datos históricos
            url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={year}-{month}-01&end_date={year}-{month}-31&timezone={timeZone}&daily={daily_params}"

            respuesta = requests.get(url)

            if respuesta.status_code == 200:
                # Convertir la respuesta JSON en un diccionario
                datos = respuesta.json()

                # Convertir la parte de "daily" en un DataFrame
                df_year = pd.DataFrame(datos["daily"])

                # Convertir la columna 'time' a datetime
                df_year["time"] = pd.to_datetime(df_year["time"])

                # Extraer año, mes y día correctamente desde la columna 'time'
                df_year["year"] = df_year["time"].dt.year
                df_year["month"] = df_year["time"].dt.month  # Corregido para extraer el mes real
                df_year["day"] = df_year["time"].dt.day  # Extraer día correctamente

                # Agregar el DataFrame a la lista
                dataframes.append(df_year)
                print(f"Datos obtenidos para el año {year}.")
            else:
                print(f"Error al consultar los datos para el año {year}. Código de estado: {respuesta.status_code}")

    # Unir los datos en un solo DataFrame
    df_datosDiarios = pd.concat(dataframes, ignore_index=True)

    # Guardar datos en un bucket de S3
    s3 = boto3.client("s3")
    nombre_bucket = os.environ.get("S3_BUCKET_NAME")  # Obtener nombre del bucket de variables de entorno
    nombre_archivo = f"datosClimaticos_{datetime.now().strftime('%Y-%m-%d')}.csv"

    # Convertimos el dataframe en un archivo CSV
    buffer_csv = df_datosDiarios.to_csv(index=False)
    s3.put_object(Bucket=nombre_bucket, Key=nombre_archivo, Body=buffer_csv)

    return {
        "statusCode": 200,
        "body": json.dumps(f"Archivo {nombre_archivo} guardado en S3 correctamente.")
    }
```
```
https://github.com/CirceDelLop/ClimaAcademiaDataEngineer/blob/main/ejercicio/awsLambda.py
```
#### Respuesta obtenida al ejecutar la funcion de Lambda
![Salida esperada.](https://i.imgur.com/PgHmmtd.png)
Una vez obtenida la respuesta espera en la función de Lambda, se corre el ETL Job del servicio Glue de AWS.
![Salida esperada.](https://i.imgur.com/rSiouC1.png)
Ya que se corrio el ETL Job, se crea un segundo archivo en S3. Los archivos generados por la función Lambda y el ETL Job de Glue se pueden observar en la siguiente imagen.
#### Archivos generados en S3
![Salida esperada.](https://i.imgur.com/xgFITx9.png)

### Histograma
![Salida esperada.](https://i.imgur.com/vpxOKUJ.png)
![Salida esperada.](https://i.imgur.com/lSc86xH.png)
### Matriz de correlación
![Salida esperada.](https://i.imgur.com/LKn4i85.png)

- Variables predictoras: Temperatura Máxima y Temperatura Minima
- Variable objetivo: Temperatura Media

### Métricas resultandes de desempeño
![Salida esperada.](https://i.imgur.com/dzBS7U4.png)

### Código ejecutado en Google Colab
```
https://colab.research.google.com/drive/1DUmGUdjaZ4_QNoYihEfWi5chv7Kj7dzK?usp=sharing
```
```
https://github.com/CirceDelLop/ClimaAcademiaDataEngineer/blob/main/ejercicio/cdl_ejercicioapiclima.py
```

### Conclusión
El uso de servicios de AWS como Glue y Lambda ayuda a la eficacia y rapidez para la obtención de datos de APIs externas, en este caso Open-Meteor.

El uso de herramientas como Google Colab, ayuda a analizar y entrenar modelos para poder obtener resultados fiables, con rapidez y a un bajo costo. Lo que hace que sea una herramienta ideal para prácticar y aprender en el área de análisis y entrenamiento.

Para poder obtener resultados optimos en las métricas, se debe tener conocimiento de que datos usar como variables predictivas y cual como variable objetivo, así como, el correcto equilibrio entre las clases que se asignen.
