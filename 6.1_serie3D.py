from pathlib import Path
import pandas as pd
import plotly.express as px


# El archivo tiene contenido de Excel aunque su extension sea .csv.
ruta_archivo = Path(__file__).with_name("Reporte_AVPF1_G1 (1).csv")
df = pd.read_excel(ruta_archivo, engine="openpyxl")
df.columns = df.columns.str.strip()
df = df.drop_duplicates()

# El dataset registra la edad de prueba, no fechas de calendario.
edad = "age"
cemento = "cement"
resistencia = "compressive_strength"
columnas_requeridas = [edad, cemento, resistencia]
columnas_faltantes = [
    columna for columna in columnas_requeridas if columna not in df.columns
]
if columnas_faltantes:
    raise KeyError(
        f"Faltan columnas requeridas en el dataset: {columnas_faltantes}"
    )

# Convertir edad, cemento y resistencia a números y quitar filas incompletas.
for columna in columnas_requeridas:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")

df = df.dropna(subset=columnas_requeridas)
if df.empty:
    raise ValueError("No hay registros válidos para generar el gráfico 3D.")

# Cada punto representa una muestra del concreto.
fig = px.scatter_3d(
    df,
    x=edad,
    y=cemento,
    z=resistencia,
    color=resistencia,
    color_continuous_scale="Viridis",
    opacity=0.8,
    hover_data={
        edad: True,
        cemento: ":.2f",
        resistencia: ":.2f",
    },
    title="Serie temporal: relación 3D entre edad, cemento y resistencia",
    labels={
        edad: "Edad del concreto (días)",
        cemento: "Cemento",
        resistencia: "Resistencia a la compresión",
    },
)
fig.update_layout(
    scene={
        "xaxis_title": "Edad del concreto (días)",
        "yaxis_title": "Cemento",
        "zaxis_title": "Resistencia a la compresión",
    }
)
fig.show()