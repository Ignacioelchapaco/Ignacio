import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os

# Imprimir el directorio actual de trabajo
st.write(f'Directorio actual de trjo: {os.getcwd()}')

# Listar los archivos en el directorio actual de trabajo
st.write('Archivos en el directorio actual:')
st.write(os.listdir('.'))

# Cambia la ruta del archivo a la ruta local correcta
file_path = '/home/ignacio/Descargas/archive/BIG FIVE 1995-2019.csv'  # Si el archivo está en el mismo directorio que el script Python
# file_path = '/ruta/completa/al/archivo/BIG FIVE 1995-2019.csv'  # Si está en otro directorio

# Cargar el archivo CSV
try:
    data = pd.read_csv(file_path)
except FileNotFoundError:
    st.error(f'El archivo {file_path} no se encontró. Por favor, verifica la ruta del archivo.')
    st.stop()

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

# Opcional: Agregar estadísticas descriptivas
if st.checkbox('Mostrar estadísticas descriptivas'):
    st.write(data_limited.describe())
