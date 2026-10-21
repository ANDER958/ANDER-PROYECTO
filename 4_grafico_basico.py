from pathlib import Path
import pandas as pd
import plotly.express as px


# El archivo tiene contenido de Excel aunque su extension sea .csv.
archivo = Path(__file__).with_name("Reporte_AVPF1_G1 (1).csv")
df = pd.read_excel(archivo, engine="openpyxl")
df.columns = df.columns.str.strip()

columna_resistencia = "compressive_strength"
columna_edad = "age"
columnas_requeridas = [columna_resistencia, columna_edad]
columnas_faltantes = [
    columna for columna in columnas_requeridas if columna not in df.columns
]

if columnas_faltantes:
    raise KeyError(f"Faltan columnas requeridas en el dataset: {columnas_faltantes}")

# Histograma de la distribución de la resistencia del concreto.
fig_histograma = px.histogram(
    df,
    x=columna_resistencia,
    nbins=30,
    title="Distribución de la resistencia del concreto",
    labels={
        columna_resistencia: "Resistencia a la compresión",
        "count": "Cantidad",
    },
)
fig_histograma.show()

# Relación entre la edad del concreto y su resistencia a la compresión.
fig_dispersion = px.scatter(
    df,
    x=columna_edad,
    y=columna_resistencia,
    title="Resistencia del concreto según su edad",
    labels={
        columna_edad: "Edad (días)",
        columna_resistencia: "Resistencia a la compresión",
    },
)
fig_dispersion.show()