from pathlib import Path
import pandas as pd
import plotly.express as px


# El archivo tiene contenido de Excel aunque su extension sea .csv.
archivo = Path(__file__).with_name("Reporte_AVPF1_G1 (1).csv")
df = pd.read_excel(archivo, engine="openpyxl")
df.columns = df.columns.str.strip()
df = df.drop_duplicates()

columna_edad = "age"
columna_cemento = "cement"
columna_resistencia = "compressive_strength"
columnas_requeridas = [columna_edad, columna_cemento, columna_resistencia]
columnas_faltantes = [
    columna for columna in columnas_requeridas if columna not in df.columns
]

if columnas_faltantes:
    raise KeyError(
        f"Faltan columnas requeridas en el dataset: {columnas_faltantes}"
    )

# Convertir a números y omitir filas con datos faltantes.
for columna in columnas_requeridas:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")

df = df.dropna(subset=columnas_requeridas)
if df.empty:
    raise ValueError("No hay registros válidos para generar el gráfico.")

# Gráfico 3D: edad, cantidad de cemento y resistencia del concreto.
fig = px.scatter_3d(
    df,
    x=columna_edad,
    y=columna_cemento,
    z=columna_resistencia,
    color=columna_resistencia,
    color_continuous_scale="Viridis",
    title="Relación 3D entre edad, cemento y resistencia del concreto",
    labels={
        columna_edad: "Edad (días)",
        columna_cemento: "Cemento",
        columna_resistencia: "Resistencia a la compresión",
    },
    opacity=0.75,
    hover_data=[columna_edad, columna_cemento, columna_resistencia],
)

fig.show()