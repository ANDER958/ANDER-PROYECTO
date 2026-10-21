from pathlib import Path

import pandas as pd


# El archivo tiene contenido de Excel aunque su extension sea .csv.
archivo = Path(__file__).with_name("Reporte_AVPF1_G1 (1).csv")
df = pd.read_excel(archivo, engine="openpyxl")
df.columns = df.columns.str.strip()

# Eliminar filas duplicadas
duplicados = int(df.duplicated().sum())
df = df.drop_duplicates()

# Columnas usadas para calcular los KPI
columna_resistencia = "compressive_strength"
columna_edad = "age"
columnas_requeridas = [columna_resistencia, columna_edad]
columnas_faltantes = [
    columna for columna in columnas_requeridas if columna not in df.columns
]

if columnas_faltantes:
    raise KeyError(f"Faltan columnas requeridas en el dataset: {columnas_faltantes}")

# Calcular KPI
resistencia_promedio = df[columna_resistencia].mean()
resistencia_maxima = df[columna_resistencia].max()
resistencia_minima = df[columna_resistencia].min()
cantidad_registros = len(df)
edad_promedio = df[columna_edad].mean()
# Mostrar resultados
print(f"Filas duplicadas eliminadas: {duplicados}")
print(f"Resistencia promedio: {resistencia_promedio:.2f}")
print(f"Resistencia máxima: {resistencia_maxima:.2f}")
print(f"Resistencia mínima: {resistencia_minima:.2f}")
print(f"Número de registros: {cantidad_registros}")
print(f"Edad promedio: {edad_promedio:.2f} días")