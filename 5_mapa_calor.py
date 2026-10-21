from pathlib import Path
import pandas as pd
import plotly.express as px

# El archivo tiene contenido de Excel aunque su extension sea .csv.
ruta_archivo = Path(__file__).with_name("Reporte_AVPF1_G1 (1).csv")
df = pd.read_excel(ruta_archivo, engine="openpyxl")
df.columns = df.columns.str.strip()
df = df.drop_duplicates()

# Usar solo las columnas numéricas para calcular las correlaciones.
datos_numericos = df.apply(pd.to_numeric, errors="coerce").dropna(
    axis=1, how="all"
)
if datos_numericos.shape[1] < 2:
    raise ValueError(
        "Se necesitan al menos dos columnas numéricas para calcular correlaciones."
    )

correlaciones = datos_numericos.corr()

# Crear un mapa de calor interactivo de las correlaciones.
fig = px.imshow(
    correlaciones,
    text_auto=".2f",
    color_continuous_scale="RdBu_r",
    zmin=-1,
    zmax=1,
    aspect="auto",
    title="Mapa de calor de correlaciones",
    labels={"x": "Variable", "y": "Variable", "color": "Correlación"},
)

fig.show()