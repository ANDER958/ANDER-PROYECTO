from pathlib import Path
import pandas as pd
import plotly.express as px

# El archivo tiene contenido de Excel aunque su extension sea .csv.
archivo = Path(__file__).with_name("Reporte_AVPF1_G1 (1).csv")
df = pd.read_excel(archivo, engine="openpyxl")
df.columns = df.columns.str.strip()
df = df.drop_duplicates()

columna_resistencia = "compressive_strength"
if columna_resistencia not in df.columns:
    raise KeyError(f"Falta la columna requerida en el dataset: {columna_resistencia}")

# Calcular las medidas de tendencia central de la resistencia.
df[columna_resistencia] = pd.to_numeric(
    df[columna_resistencia], errors="coerce"
)
resistencia = df[columna_resistencia].dropna()
if resistencia.empty:
    raise ValueError("No hay valores numéricos válidos de resistencia.")

media = resistencia.mean()
mediana = resistencia.median()
modas = resistencia.mode()
desviacion_estandar = resistencia.std()

print(f"Media de la resistencia: {media:.2f}")
print(f"Mediana de la resistencia: {mediana:.2f}")
print(f"Desviación estándar de la resistencia: {desviacion_estandar:.2f}")
print(
    "Moda(s) de la resistencia: "
    + ", ".join(f"{valor:g}" for valor in modas)
)

# Crear primero el histograma; luego se agregan las líneas estadísticas.
fig_histograma = px.histogram(
    pd.DataFrame({columna_resistencia: resistencia}),
    x=columna_resistencia,
    nbins=30,
    title="Distribución de resistencia: media, mediana y moda",
    labels={
        columna_resistencia: "Resistencia a la compresión",
        "count": "Cantidad de registros",
    },
)

# Añadir al histograma las líneas de media, mediana y moda.
fig_histograma.add_vline(
    x=media,
    line_dash="dash",
    line_color="red",
    annotation_text=f"Media: {media:.2f}",
    annotation_position="top",
)

fig_histograma.add_vline(
    x=mediana,
    line_dash="dot",
    line_color="green",
    annotation_text=f"Mediana: {mediana:.2f}",
    annotation_position="top left",
)

for moda in modas:
    fig_histograma.add_vline(
        x=moda,
        line_dash="longdash",
        line_color="blue",
        annotation_text=f"Moda: {moda:g}",
        annotation_position="bottom",
    )

fig_histograma.show()