#importar librerias
from pathlib import Path
import pandas as pd
#cargar el dataset
archivo = Path(__file__).with_name("Reporte_AVPF1_G1 (1).csv")
df = pd.read_excel(archivo, engine="openpyxl")
#visualizar la informacion
print(df.head()) #muestra las primeras 5 filas
df.info()       #muestra columnas, tipos de datos y valores no nulos
print(df.shape) #muestra (cantidad de filas, candtidad de columnas)