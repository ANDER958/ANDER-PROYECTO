from math import ceil
from pathlib import Path
import numpy as np
import pandas as pd


# El archivo tiene contenido de Excel aunque su extension sea .csv.
ruta_archivo = Path(__file__).with_name("Reporte_AVPF1_G1 (1).csv")
df = pd.read_excel(ruta_archivo, engine="openpyxl")
df.columns = df.columns.str.strip()
df = df.drop_duplicates()

# Usar la edad de ensayo junto con los componentes de la mezcla para predecir
# la resistencia a la compresión.
columnas_entrada = [
    "cement",
    "furnace_slag",
    "fly_ash",
    "water",
    "super_plasticizer",
    "Coarse Aggregate  (component 6)(kg in a m^3 mixture)",
    "fine_agg",
    "age",
]
columna_objetivo = "compressive_strength"
columnas_requeridas = columnas_entrada + [columna_objetivo]
columnas_faltantes = [
    columna for columna in columnas_requeridas if columna not in df.columns
]
if columnas_faltantes:
    raise KeyError(
        f"Faltan columnas requeridas en el dataset: {columnas_faltantes}"
    )

for columna in columnas_requeridas:
    df[columna] = pd.to_numeric(df[columna], errors="coerce")

datos = df[columnas_requeridas].dropna()
if len(datos) < 5:
    raise ValueError(
        "Se necesitan al menos 5 registros completos para entrenar y evaluar el modelo."
    )


def ajustar_modelo(X, y):
    """Ajusta una regresión lineal múltiple, incluyendo el intercepto."""
    X_con_intercepto = np.column_stack((np.ones(len(X)), X))
    coeficientes, _, _, _ = np.linalg.lstsq(X_con_intercepto, y, rcond=None)
    return coeficientes


def predecir(X, coeficientes):
    X_con_intercepto = np.column_stack((np.ones(len(X)), X))
    return X_con_intercepto @ coeficientes


X = datos[columnas_entrada].to_numpy(dtype=float)
y = datos[columna_objetivo].to_numpy(dtype=float)

# Reservar registros para evaluar el modelo con datos no entrenados.
indices = np.random.default_rng(42).permutation(len(datos))
cantidad_prueba = min(max(1, ceil(len(datos) * 0.2)), len(datos) - 2)
indices_prueba = indices[:cantidad_prueba]
indices_entrenamiento = indices[cantidad_prueba:]

coeficientes_prueba = ajustar_modelo(
    X[indices_entrenamiento], y[indices_entrenamiento]
)
predicciones_prueba = predecir(X[indices_prueba], coeficientes_prueba)
y_prueba = y[indices_prueba]

mae = np.mean(np.abs(y_prueba - predicciones_prueba))
print(f"Registros utilizados: {len(datos)}")
print(f"Variables de entrada: {', '.join(columnas_entrada)}")
print(f"Error absoluto medio (MAE) en prueba: {mae:.2f}")

if len(y_prueba) >= 2 and np.sum((y_prueba - y_prueba.mean()) ** 2) > 0:
    r2_prueba = 1 - (
        np.sum((y_prueba - predicciones_prueba) ** 2)
        / np.sum((y_prueba - y_prueba.mean()) ** 2)
    )
    print(f"R² en el conjunto de prueba: {r2_prueba:.4f}")
else:
    print(
        "R² en prueba no disponible: faltan datos o variación en las resistencias de prueba."
    )

# Entrenar el modelo definitivo con todos los registros disponibles.
coeficientes_finales = ajustar_modelo(X, y)

# Ejemplo: predecir usando una mezcla promedio y la edad promedio del dataset.
mezcla_ejemplo = datos[columnas_entrada].mean().to_frame().T
prediccion = predecir(
    mezcla_ejemplo.to_numpy(dtype=float), coeficientes_finales
)[0]
print(
    "Resistencia estimada para una mezcla y edad promedio: "
    f"{prediccion:.2f}"
)