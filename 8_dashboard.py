import os
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import pandas as pd


CARPETA = Path(__file__).resolve().parent
DATASET = CARPETA / "Reporte_AVPF1_G1 (1).csv"

# Permite iniciar el dashboard ejecutando este archivo con Python.
if os.environ.get("CONCRETE_DASHBOARD_STREAMLIT") != "1":
    entorno = os.environ.copy()
    entorno["CONCRETE_DASHBOARD_STREAMLIT"] = "1"
    subprocess.run(
        [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            str(Path(__file__).resolve()),
            "--server.headless",
            "true",
        ],
        cwd=CARPETA,
        env=entorno,
        check=True,
    )
    raise SystemExit

import streamlit as st


@st.cache_data(max_entries=3)
def cargar_dataset(contenido: bytes) -> pd.DataFrame:
    """Lee CSV y libros Excel, incluso si el libro tiene extension .csv."""
    if contenido.startswith(b"PK\x03\x04"):
        return pd.read_excel(BytesIO(contenido), engine="openpyxl")

    try:
        return pd.read_csv(BytesIO(contenido), encoding="utf-8-sig")
    except UnicodeDecodeError:
        return pd.read_csv(BytesIO(contenido), encoding="cp1252")


st.set_page_config(
    page_title="Resistencia del concreto",
    page_icon="🏗️",
    layout="wide",
)
st.title("Dashboard de resistencia del concreto")
st.caption("Indicadores, análisis de mezclas y comportamiento de la resistencia")

archivo = st.sidebar.file_uploader(
    "Cargar otro archivo CSV o Excel",
    type=["csv", "xlsx"],
)
if archivo is not None:
    df = cargar_dataset(archivo.getvalue())
elif DATASET.is_file():
    df = cargar_dataset(DATASET.read_bytes())
else:
    st.error(f"No se encontró el dataset: {DATASET.name}")
    st.stop()

df.columns = df.columns.astype(str).str.strip()
df = df.drop_duplicates()

for columna in df.columns:
    valores = pd.to_numeric(df[columna], errors="coerce")
    if valores.notna().any():
        df[columna] = valores


def buscar_columna(*fragmentos: str) -> str | None:
    nombres = {str(columna).casefold(): columna for columna in df.columns}
    for fragmento in fragmentos:
        if fragmento.casefold() in nombres:
            return nombres[fragmento.casefold()]
    for columna in df.columns:
        if any(
            fragmento.casefold() in str(columna).casefold()
            for fragmento in fragmentos
        ):
            return columna
    return None


edad_col = buscar_columna("age")
resistencia_col = buscar_columna("compressive_strength", "compressive strength")
if resistencia_col is None:
    resistencia_col = buscar_columna("strength")

if edad_col is None or resistencia_col is None:
    st.error(
        "El dataset debe incluir columnas de edad y resistencia a la compresión."
    )
    st.write("Columnas encontradas:", list(df.columns))
    st.stop()

df[edad_col] = pd.to_numeric(df[edad_col], errors="coerce")
df[resistencia_col] = pd.to_numeric(df[resistencia_col], errors="coerce")
df = df.dropna(subset=[edad_col, resistencia_col])
if df.empty:
    st.error("El dataset no contiene edades y resistencias numéricas válidas.")
    st.stop()

componentes = {
    "Cemento": ("cement",),
    "Agua": ("water",),
    "Agregado grueso": ("coarse aggregate",),
    "Agregado fino": ("fine_agg", "fine aggregate"),
    "Superplastificante": ("super_plasticizer", "superplasticizer"),
    "Escoria de alto horno": ("furnace_slag", "slag"),
    "Ceniza volante": ("fly_ash", "fly ash"),
    "Relación agua/cemento": ("water_cement_ratio",),
}
columnas_mezcla = {
    nombre: columna
    for nombre, fragmentos in componentes.items()
    if (columna := buscar_columna(*fragmentos)) is not None
}

with st.sidebar:
    st.header("Filtros")
    edad_min = float(df[edad_col].min())
    edad_max = float(df[edad_col].max())
    if edad_min < edad_max:
        rango_edad = st.slider(
            "Edad del concreto (días)",
            min_value=edad_min,
            max_value=edad_max,
            value=(edad_min, edad_max),
            step=1.0,
        )
    else:
        rango_edad = (edad_min, edad_max)

datos = df[df[edad_col].between(*rango_edad)].copy()
if datos.empty:
    st.warning("No hay muestras para el rango de edad seleccionado.")
    st.stop()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Muestras", f"{len(datos):,}", border=True)
k2.metric(
    "Resistencia promedio",
    f"{datos[resistencia_col].mean():.2f}",
    border=True,
)
k3.metric(
    "Resistencia máxima",
    f"{datos[resistencia_col].max():.2f}",
    border=True,
)
k4.metric("Edad promedio", f"{datos[edad_col].mean():.1f} días", border=True)

izquierda, derecha = st.columns(2)
with izquierda:
    st.subheader("Resistencia promedio según edad")
    resistencia_por_edad = (
        datos.groupby(edad_col, as_index=False)[resistencia_col]
        .mean()
        .sort_values(edad_col)
    )
    st.line_chart(
        resistencia_por_edad,
        x=edad_col,
        y=resistencia_col,
        x_label="Edad del concreto (días)",
        y_label="Resistencia promedio",
        alt="Resistencia promedio a la compresión por edad del concreto",
    )

with derecha:
    st.subheader("Distribución de la resistencia")
    histograma = (
        pd.cut(datos[resistencia_col], bins=12)
        .value_counts()
        .sort_index()
    )
    datos_histograma = pd.DataFrame(
        {
            "Rango de resistencia": histograma.index.astype(str),
            "Cantidad de muestras": histograma.values,
        }
    )
    st.bar_chart(
        datos_histograma,
        x="Rango de resistencia",
        y="Cantidad de muestras",
        x_label="Rango de resistencia",
        y_label="Cantidad de muestras",
        alt="Distribución de las muestras por rango de resistencia",
    )

if columnas_mezcla:
    st.subheader("Influencia de los componentes de la mezcla")
    nombre_componente = st.selectbox(
        "Selecciona un componente",
        list(columnas_mezcla),
    )
    columna_componente = columnas_mezcla[nombre_componente]
    datos_dispersion = datos.dropna(
        subset=[columna_componente, resistencia_col]
    )
    if datos_dispersion.empty:
        st.warning("No hay datos válidos para el componente seleccionado.")
    else:
        st.scatter_chart(
            datos_dispersion,
            x=columna_componente,
            y=resistencia_col,
            x_label=nombre_componente,
            y_label="Resistencia a la compresión",
            alt=f"Relación entre {nombre_componente.lower()} y resistencia",
        )

    st.subheader("Composición promedio de las mezclas")
    promedios = datos[list(columnas_mezcla.values())].mean()
    promedios.index = list(columnas_mezcla.keys())
    st.bar_chart(
        promedios,
        x_label="Componente",
        y_label="Promedio",
        alt="Promedio de cada componente de la mezcla",
    )

st.subheader("Correlación entre variables")
numericas = datos.select_dtypes(include="number")
if len(numericas.columns) > 1:
    st.dataframe(
        numericas.corr().round(2),
        width="stretch",
        alt="Matriz de correlación entre variables numéricas",
    )
else:
    st.info("No hay suficientes columnas numéricas para calcular correlaciones.")

st.subheader("Datos de las muestras")
st.dataframe(
    datos,
    hide_index=True,
    width="stretch",
    alt="Registros del dataset filtrados por edad",
)
st.download_button(
    "Descargar datos filtrados",
    datos.to_csv(index=False).encode("utf-8"),
    file_name="muestras_concreto_filtradas.csv",
    mime="text/csv",
    width="stretch",
)