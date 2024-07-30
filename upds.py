import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import gdown

# Descargar el archivo CSV desde Google Drive
file_url = 'https://drive.google.com/uc?id=1eCvay0DQLM5giVzPCgW6gdbPmAfhsYvs'
file_path = 'BIG_FIVE_1995-2019.csv'

if not os.path.exists(file_path):
    gdown.download(file_url, file_path, quiet=False)

# Cargar el archivo CSV
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f'El archivo {file_path} no se encontró. Por favor, verifica la ruta del archivo.')
    st.stop()

# Imprimir el directorio actual de trabajo
st.write(f'Directorio actual de trabajo: {os.getcwd()}')

# Listar los archivos en el directorio actual de trabajo
st.write('Archivos en el directorio actual:')
st.write(os.listdir('.'))

# Seleccionar el número de filas a mostrar
num_rows = st.slider('Selecciona el número de filas a mostrar:', min_value=1, max_value=len(data), value=100)

# Limitar los datos al número de filas seleccionado
data_limited = data.head(num_rows)

# Mostrar los primeros registros del DataFrame
st.write(data_limited.head())

# Seleccionar el tipo de gráfico
chart_type = st.selectbox('Selecciona el tipo de gráfico:', ['Línea', 'Barra', 'Dispersión'])

# Seleccionar las columnas para el gráfico
columns = data.columns.tolist()
x_axis = st.selectbox('Selecciona la columna para el eje X:', columns)
y_axis = st.selectbox('Selecciona la columna para el eje Y:', columns)

# Crear el gráfico basado en la selección del usuario
if chart_type == 'Línea':
    fig, ax = plt.subplots()
    ax.plot(data_limited[x_axis], data_limited[y_axis])
    ax.set_xlabel(x_axis)
    ax.set_ylabel(y_axis)
    ax.set_title(f'Gráfico de línea de {x_axis} vs {y_axis}')
    st.pyplot(fig)
elif chart_type == 'Barra':
    fig = px.bar(data_limited, x=x_axis, y=y_axis, title=f'Gráfico de barra de {x_axis} vs {y_axis}')
    st.plotly_chart(fig)
elif chart_type == 'Dispersión':
    fig = px.scatter(data_limited, x=x_axis, y=y_axis, title=f'Gráfico de dispersión de {x_axis} vs {y_axis}')
    st.plotly_chart(fig)

# Calcular regresión lineal y R^2
X = data_limited[[x_axis]].values
y = data_limited[y_axis].values

model = LinearRegression()
model.fit(X, y)
y_pred = model.predict(X)
r2 = r2_score(y, y_pred)

# Mostrar la regresión lineal y R^2
st.write(f'Regresión lineal: {x_axis} vs {y_axis}')
st.write(f'Coeficiente de regresión (pendiente): {model.coef_[0]}')
st.write(f'Intersección: {model.intercept_}')
st.write(f'R^2: {r2*100:.2f}%')

# Graficar la regresión lineal
fig, ax = plt.subplots()
ax.scatter(data_limited[x_axis], data_limited[y_axis], label='Datos')
ax.plot(data_limited[x_axis], y_pred, color='red', label='Regresión lineal')
ax.set_xlabel(x_axis)
ax.set_ylabel(y_axis)
ax.set_title(f'Regresión lineal de {x_axis} vs {y_axis}')
ax.legend()
st.pyplot(fig)

# Opcional: Agregar estadísticas descriptivas
if st.checkbox('Mostrar estadísticas descriptivas'):
    st.write(data_limited.describe())
