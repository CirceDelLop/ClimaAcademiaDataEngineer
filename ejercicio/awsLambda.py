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
    years = [2023, 2024, 2025]
    month = "01"

    # Lista de parámetros a solicitar
    daily_params = "temperature_2m_max,temperature_2m_min,temperature_2m_mean,rain_sum,precipitation_hours,wind_speed_10m_max,shortwave_radiation_sum"

    # Lista para almacenar DataFrames
    dataframes = []

    for year in years:
        # Solicitud a la API de Open-Meteo para obtener los datos históricos
        url = f"https://archive-api.open-meteo.com/v1/archive?latitude={latitude}&longitude={longitude}&start_date={year}-{month}-01&end_date={year}-{month}-27&timezone={timeZone}&daily={daily_params}"
        
        print(f"Consultando: {url}")  # Debugging

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