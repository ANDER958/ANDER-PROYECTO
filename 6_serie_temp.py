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
resistencia = "compressive_strength"
columnas_requeridas = [edad, resistencia]
columnas_faltantes = [
    columna for columna in columnas_requeridas if columna not in df.columns
]
if columnas_faltantes:
    raise KeyError(
        f"Faltan columnas requeridas en el dataset: {columnas_faltantes}"
    )

# Convertir edad y resistencia a números y quitar filas incompletas.
for columna in columnas_requeridas:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")

df = df.dropna(subset=columnas_requeridas)
if df.empty:
    raise ValueError("No hay registros válidos para generar la serie temporal.")

# Calcular la resistencia promedio para cada edad y ordenar el eje temporal.
resistencia_por_edad = (
    df.groupby(edad, as_index=False)[resistencia]
    .mean()
    .sort_values(edad)
)

fig = px.line(
    resistencia_por_edad,
    x=edad,
    y=resistencia,
    markers=True,
    title="Evolución de la resistencia promedio según la edad del concreto",
    labels={
        edad: "Edad del concreto (días)",
        resistencia: "Resistencia a la compresión",
    },
)
fig.update_traces(line={"color": "royalblue", "width": 3})
fig.update_layout(
    xaxis_title="Edad del concreto (días)",
    yaxis_title="Resistencia promedio",
)
fig.show()