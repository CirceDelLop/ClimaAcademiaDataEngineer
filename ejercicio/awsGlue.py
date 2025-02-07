import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql import DataFrame
import boto3

# Inicializar el contexto de Spark y Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Parámetros de entrada
args = getResolvedOptions(sys.argv, ['S3_INPUT_PATH', 'S3_OUTPUT_PATH'])
input_path = args['S3_INPUT_PATH']
output_path = args['S3_OUTPUT_PATH']

# Cargar datos desde S3
df = spark.read.format("csv").option("header", "true").load(input_path)

# Agregar una columna ID autoincremental
df = df.withColumn("ID", F.monotonically_increasing_id())

# Guardar los datos procesados en S3
df.write.mode("overwrite").option("header", "true").csv(output_path)

job.commit()
