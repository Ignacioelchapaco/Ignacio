import os
import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import matplotlib.pyplot as plt

class ETLGUI:
    def __init__(self, master):
        self.master = master
        master.title("Proceso ETL")
        master.geometry("600x650")  # Aumento de altura para incluir el nuevo campo

        # Widgets
        self.folder_path = tk.StringVar()
        self.folder_label = tk.Label(master, text="Carpeta de datos:")
        self.folder_entry = tk.Entry(master, textvariable=self.folder_path, width=50)
        self.folder_button = tk.Button(master, text="Seleccionar", command=self.select_folder)

        self.col_range_label = tk.Label(master, text="Rango de columnas (ej. A:D):")
        self.col_range_entry = tk.Entry(master)

        self.start_row_label = tk.Label(master, text="Fila inicial:")
        self.start_row_entry = tk.Entry(master)

        self.row_limit_label = tk.Label(master, text="Límite de filas (opcional):")
        self.row_limit_entry = tk.Entry(master)  # Nuevo campo para el límite de filas

        self.process_button = tk.Button(master, text="Procesar", command=self.process_data)

        # Botones para gráficos
        self.pie_chart_button = tk.Button(master, text="Generar Gráfica de Torta", command=self.generate_pie_chart)
        self.bar_chart_button = tk.Button(master, text="Generar Gráfica de Barras", command=self.generate_bar_chart)

        self.progress_bar = ttk.Progressbar(master, orient="horizontal", length=300, mode="determinate")

        # Layout
        self.folder_label.pack(pady=5)
        self.folder_entry.pack(pady=5)
        self.folder_button.pack(pady=5)
        self.col_range_label.pack(pady=5)
        self.col_range_entry.pack(pady=5)
        self.start_row_label.pack(pady=5)
        self.start_row_entry.pack(pady=5)
        self.row_limit_label.pack(pady=5)
        self.row_limit_entry.pack(pady=5)  # Agregar el campo de límite de filas
        self.process_button.pack(pady=10)
        self.pie_chart_button.pack(pady=10)
        self.bar_chart_button.pack(pady=10)
        self.progress_bar.pack(pady=10)

        # Store the processed DataFrame
        self.final_df = None

    def select_folder(self):
        folder_selected = filedialog.askdirectory()
        self.folder_path.set(folder_selected)

    def process_data(self):
        folder_path = self.folder_path.get()
        col_range = self.col_range_entry.get()
        start_row = int(self.start_row_entry.get()) - 1  # Ajustar para índice basado en 0
        row_limit = self.row_limit_entry.get()

        if row_limit:
            try:
                row_limit = int(row_limit)
            except ValueError:
                messagebox.showerror("Error", "El límite de filas debe ser un número entero.")
                return
        else:
            row_limit = None

        if not folder_path or not col_range or not start_row:
            messagebox.showerror("Error", "Por favor, complete todos los campos.")
            return

        try:
            # Obtener la lista de archivos Excel en la carpeta
            excel_files = [f for f in os.listdir(folder_path) if f.endswith('.xlsx') and f.startswith('AvanceVentasINTI')]

            if not excel_files:
                messagebox.showerror("Error", "No se encontraron archivos Excel en la carpeta seleccionada.")
                return

            all_data = []
            self.progress_bar["maximum"] = len(excel_files)

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

                # Actualizar la barra de progreso
                self.progress_bar["value"] = i + 1
                self.master.update_idletasks()

            # Consolidar todos los DataFrames
            self.final_df = pd.concat(all_data, ignore_index=True)

            # Exportar a Excel
            output_path = os.path.join(folder_path, 'Out.xlsx')
            self.final_df.to_excel(output_path, index=False)

            messagebox.showinfo("Éxito", f"Proceso completado. Archivo guardado en {output_path}")

            # Mostrar el DataFrame final
            self.show_dataframe(self.final_df)

        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error durante el proceso: {str(e)}")

    def show_dataframe(self, df):
        # Crear una nueva ventana para mostrar el DataFrame
        data_window = tk.Toplevel(self.master)
        data_window.title("Dataset Final")
        data_window.geometry("800x600")

        # Crear un widget Text para mostrar el DataFrame
        text_widget = tk.Text(data_window)
        text_widget.pack(expand=True, fill='both')

        # Insertar el DataFrame en el widget Text
        text_widget.insert(tk.END, df.to_string())

    def generate_pie_chart(self):
        if self.final_df is None:
            messagebox.showerror("Error", "Primero debe procesar los datos.")
            return

        # Identificar columnas que pueden ser usadas para gráficas de torta
        categorical_cols = self.final_df.select_dtypes(include=[object]).columns.tolist()
        numeric_cols = self.final_df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = categorical_cols + numeric_cols
        if not all_cols:
            messagebox.showerror("Error", "No se encontraron columnas para graficar.")
            return

        # Crear una ventana para seleccionar la columna a graficar
        select_window = tk.Toplevel(self.master)
        select_window.title("Seleccionar Columna para Gráfico de Torta")
        select_window.geometry("300x150")

        tk.Label(select_window, text="Seleccione la columna para graficar:").pack(pady=10)

        column_var = tk.StringVar(select_window)
        column_var.set(all_cols[0])  # valor por defecto
        column_menu = tk.OptionMenu(select_window, column_var, *all_cols)
        column_menu.pack(pady=10)

        def on_select():
            selected_column = column_var.get()
            select_window.destroy()
            self.create_pie_chart(selected_column)

        tk.Button(select_window, text="Graficar", command=on_select).pack(pady=10)

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
        output_folder = self.folder_path.get()
        output_path = os.path.join(output_folder, f'distribucion_{column}.png')
        plt.savefig(output_path)
        plt.close()

        messagebox.showinfo("Éxito", f"Gráfica guardada en {output_path}")

    def generate_bar_chart(self):
        if self.final_df is None:
            messagebox.showerror("Error", "Primero debe procesar los datos.")
            return

        # Identificar columnas que pueden ser usadas para gráficas de barras
        categorical_cols = self.final_df.select_dtypes(include=[object]).columns.tolist()
        numeric_cols = self.final_df.select_dtypes(include=[np.number]).columns.tolist()
        all_cols = categorical_cols + numeric_cols
        if not all_cols:
            messagebox.showerror("Error", "No se encontraron columnas para graficar.")
            return

        # Crear una ventana para seleccionar la columna a graficar
        select_window = tk.Toplevel(self.master)
        select_window.title("Seleccionar Columna para Gráfico de Barras")
        select_window.geometry("300x150")

        tk.Label(select_window, text="Seleccione la columna para graficar:").pack(pady=10)

        column_var = tk.StringVar(select_window)
        column_var.set(all_cols[0])  # valor por defecto
        column_menu = tk.OptionMenu(select_window, column_var, *all_cols)
        column_menu.pack(pady=10)

        def on_select():
            selected_column = column_var.get()
            select_window.destroy()
            self.create_bar_chart(selected_column)

        tk.Button(select_window, text="Graficar", command=on_select).pack(pady=10)

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
        output_folder = self.folder_path.get()
        output_path = os.path.join(output_folder, f'frecuencia_{column}.png')
        plt.savefig(output_path)
        plt.close()

        messagebox.showinfo("Éxito", f"Gráfica guardada en {output_path}")

if __name__ == "__main__":
    root = tk.Tk()
    etl_gui = ETLGUI(root)
    root.mainloop()
