import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import io

class ETLApp:
    def __init__(self):
        self.final_df = None

    def upload_file(self):
        uploaded_file = st.file_uploader("Sube un archivo CSV o XLSX", type=['csv', 'xlsx'])
        if uploaded_file is not None:
            if uploaded_file.type == "text/csv":
                # Leer archivo CSV
                self.final_df = pd.read_csv(uploaded_file)
            elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                # Leer archivo XLSX
                self.final_df = pd.read_excel(uploaded_file)
            st.success("Archivo cargado exitosamente.")
        else:
            st.info("Por favor, sube un archivo.")

    def process_data(self, col_range, start_row, row_limit):
        if self.final_df is None:
            st.error("Primero debe cargar un archivo.")
            return

        if not col_range or not start_row:
            st.error("Por favor, complete todos los campos.")
            return

        try:
            start_row = int(start_row) - 1  # Ajustar para índice basado en 0
            row_limit = int(row_limit) if row_limit else None
        except ValueError:
            st.error("El límite de filas debe ser un número entero.")
            return

        try:
            # Aplicar filtros si hay columnas y filas definidas
            if col_range:
                # Convertir rango de columnas (ej. 'A:D') a índices de columnas
                col_range = pd.io.parsers.ParserBase({'usecols': col_range})._get_usecols()
                self.final_df = self.final_df.iloc[start_row:start_row + row_limit, col_range]

            output_path = "Out.xlsx"
            self.final_df.to_excel(output_path, index=False)

            st.success(f"Proceso completado. Archivo guardado en {output_path}")

        except Exception as e:
            st.error(f"Ocurrió un error durante el proceso: {str(e)}")

    def generate_pie_chart(self, column):
        if self.final_df is None:
            st.error("Primero debe procesar los datos.")
            return

        if self.final_df[column].dtype == object:
            counts = self.final_df[column].dropna().value_counts()
        else:
            series = self.final_df[column].dropna()
            series = series[series != float('inf')]
            rounded_values = series.round().astype(int)
            counts = rounded_values.value_counts()

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
        ax.set_title(f'Distribución de {column}')
        ax.axis('equal')

        st.pyplot(fig)

    def generate_bar_chart(self, column):
        if self.final_df is None:
            st.error("Primero debe procesar los datos.")
            return

        if self.final_df[column].dtype == object:
            counts = self.final_df[column].dropna().value_counts()
        else:
            series = self.final_df[column].dropna()
            series = series[series != float('inf')]
            rounded_values = series.round().astype(int)
            counts = rounded_values.value_counts()

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(counts.index, counts.values)
        ax.set_title(f'Frecuencia de Valores en {column}')
        ax.set_xlabel('Valores')
        ax.set_ylabel('Frecuencia')
        ax.grid(True, axis='y')

        st.pyplot(fig)

def main():
    st.title("ETL Console Application")

    etl_app = ETLApp()

    st.sidebar.header("Cargar Archivo")
    etl_app.upload_file()

    if etl_app.final_df is not None:
        st.sidebar.header("Configuración de Datos")
        col_range = st.sidebar.text_input("Ingrese el rango de columnas (ej. A:D):")
        start_row = st.sidebar.text_input("Ingrese la fila inicial:")
        row_limit = st.sidebar.text_input("Ingrese el límite de filas (opcional):")

        if st.sidebar.button("Procesar Datos"):
            etl_app.process_data(col_range, start_row, row_limit)

        if etl_app.final_df is not None:
            st.sidebar.header("Generar Gráficas")
            all_cols = etl_app.final_df.columns.tolist()
            option = st.sidebar.selectbox("Seleccione el tipo de gráfica", ["Gráfica de Torta", "Gráfica de Barras"])

            if option == "Gráfica de Torta":
                selected_column = st.sidebar.selectbox("Seleccione la columna para graficar", all_cols)
                if st.sidebar.button("Generar Gráfica de Torta"):
                    etl_app.generate_pie_chart(selected_column)

            elif option == "Gráfica de Barras":
                selected_column = st.sidebar.selectbox("Seleccione la columna para graficar", all_cols)
                if st.sidebar.button("Generar Gráfica de Barras"):
                    etl_app.generate_bar_chart(selected_column)

if __name__ == "__main__":
    main()
