#importar librerias
from pathlib import Path
import pandas as pd

#cargar el dataset
df = pd.read_csv("Reporte_AVPF1_G1 (1).csv")

#visualizar la informacion
print(df.head()) #muestra las primeras 5 filas
df.info()       #muestra columnas, tipos de datos y valores no nulos
print(df.shape) #muestra (cantidad de filas, candtidad de columnas)

#limpieza rapida
print("valores nulos por columna:")
print(df.isnull().sum()) #muestra la cantidad de valores nulos por columna

duplicados = df.duplicated().sum() #muestra la cantidad de filas duplicadas
print(f"Filas duplicadas: {duplicados}")

df = df.drop_duplicates()
print(f"filas duplicadas eliminadas: {duplicados}")
print(f"dimensiones despues de eliminar duplicados: {df.shape}")