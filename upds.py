import os
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

class ETLConsole:
    def __init__(self):
        self.final_df = None

    def select_folder(self):
        folder_path = input("Ingrese la ruta de la carpeta de datos: ")
        if not os.path.isdir(folder_path):
            print("La carpeta no existe. Por favor, inténtelo de nuevo.")
            return None
        return folder_path

    def get_input(self, prompt):
        return input(prompt)

    def process_data(self):
        folder_path = self.select_folder()
        if folder_path is None:
            return

        col_range = self.get_input("Ingrese el rango de columnas (ej. A:D): ")
        start_row = self.get_input("Ingrese la fila inicial: ")
        row_limit = self.get_input("Ingrese el límite de filas (opcional): ")

        try:
            start_row = int(start_row) - 1  # Ajustar para índice basado en 0
            row_limit = int(row_limit) if row_limit else None
        except ValueError:
            print("El límite de filas debe ser un número entero.")
            return

        if not folder_path or not col_range or not start_row:
            print("Por favor, complete todos los campos.")
            return

        try:
            # Obtener la lista de archivos Excel en la carpeta
            excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and f.startswith('AvanceVentasINTI')]

            if not excel_files:
                print("No se encontraron archivos Excel en la carpeta seleccionada.")
                return

            all_data = []
            total_files = len(excel_files)

            for i, file in enumerate(excel_files):
                file_path = os.path.join(folder_path, file)
                # Extraer año, mes y día del nombre del archivo
                date_str = file.split('.')[1:4]
                year, month, day = date_str

                # Leer el archivo Excel
                df = pd.read_excel(file_path, sheet_name='ITEM_O', usecols=col_range, skiprows=start_row, nrows=row_limit)

                # Añadir columnas de año, mes y día
                df['Year'] = year
                df['Month'] = month
                df['Day'] = day

                all_data.append(df)

                # Mostrar progreso en consola
                print(f"Procesado {i + 1} de {total_files} archivos.")

            # Consolidar todos los DataFrames
            self.final_df = pd.concat(all_data, ignore_index=True)

            # Exportar a Excel
            output_path = os.path.join(folder_path, 'Out.xlsx')
            self.final_df.to_excel(output_path, index=False)

            print(f"Proceso completado. Archivo guardado en {output_path}")

        except Exception as e:
            print(f"Ocurrió un error durante el proceso: {str(e)}")

    def generate_pie_chart(self):
        if self.final_df is None:
            print("Primero debe procesar los datos.")
            return

        # Identificar columnas que pueden ser usadas para gráficas de torta
        categorical_cols = self.final_df.select_dtypes(include=[object]).columns.tolist()
        numeric_cols = self.final_df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = categorical_cols + numeric_cols
        if not all_cols:
            print("No se encontraron columnas para graficar.")
            return

        print("Seleccione la columna para graficar (índice):")
        for i, col in enumerate(all_cols):
            print(f"{i}: {col}")
        col_index = int(input("Ingrese el índice de la columna: "))
        selected_column = all_cols[col_index]

        self.create_pie_chart(selected_column)

    def create_pie_chart(self, column):
        # Manejo de valores no finitos para columnas categóricas
        if self.final_df[column].dtype == object:
            counts = self.final_df[column].dropna().value_counts()
        else:
            series = self.final_df[column].dropna()  # Eliminar NA
            series = series[series != float('inf')]  # Eliminar inf
            rounded_values = series.round().astype(int)
            counts = rounded_values.value_counts()

        # Crear la gráfica de torta
        plt.figure(figsize=(8, 8))
        plt.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140)
        plt.title(f'Distribución de {column}')
        plt.axis('equal')  # Igualar el aspecto para que sea un círculo

        # Guardar la gráfica
        output_folder = self.select_folder()
        output_path = os.path.join(output_folder, f'distribucion_{column}.png')
        plt.savefig(output_path)
        plt.close()

        print(f"Gráfica guardada en {output_path}")

    def generate_bar_chart(self):
        if self.final_df is None:
            print("Primero debe procesar los datos.")
            return

        # Identificar columnas que pueden ser usadas para gráficas de barras
        categorical_cols = self.final_df.select_dtypes(include=[object]).columns.tolist()
        numeric_cols = self.final_df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = categorical_cols + numeric_cols
        if not all_cols:
            print("No se encontraron columnas para graficar.")
            return

        print("Seleccione la columna para graficar (índice):")
        for i, col in enumerate(all_cols):
            print(f"{i}: {col}")
        col_index = int(input("Ingrese el índice de la columna: "))
        selected_column = all_cols[col_index]

        self.create_bar_chart(selected_column)

    def create_bar_chart(self, column):
        # Manejo de valores no finitos para columnas categóricas
        if self.final_df[column].dtype == object:
            counts = self.final_df[column].dropna().value_counts()
        else:
            series = self.final_df[column].dropna()  # Eliminar NA
            series = series[series != float('inf')]  # Eliminar inf
            rounded_values = series.round().astype(int)
            counts = rounded_values.value_counts()

        # Crear la gráfica de barras
        plt.figure(figsize=(10, 6))
        plt.bar(counts.index, counts.values)
        plt.title(f'Frecuencia de Valores en {column}')
        plt.xlabel('Valores')
        plt.ylabel('Frecuencia')
        plt.grid(True, axis='y')

        # Guardar la gráfica
        output_folder = self.select_folder()
        output_path = os.path.join(output_folder, f'frecuencia_{column}.png')
        plt.savefig(output_path)
        plt.close()

        print(f"Gráfica guardada en {output_path}")

if __name__ == "__main__":
    etl_console = ETLConsole()

    while True:
        print("\n--- Menú Principal ---")
        print("1. Procesar Datos")
        print("2. Generar Gráfica de Torta")
        print("3. Generar Gráfica de Barras")
        print("4. Salir")
        option = input("Seleccione una opción: ")

        if option == "1":
            etl_console.process_data()
        elif option == "2":
            etl_console.generate_pie_chart()
        elif option == "3":
            etl_console.generate_bar_chart()
        elif option == "4":
            break
        else:
            print("Opción no válida. Intente de nuevo.")
