import streamlit as st
import functions as f
import forms
import pandas as pd
import time


# Configuración de la página
st.set_page_config(layout="wide",
                         page_title='Articulos',
                         page_icon='📚')
st.markdown("# Artículos 📚")
st.sidebar.markdown("# Artículos 📚")

# Cargar la base de datos (Articulos)
# Usamos st.session_state para almacenar db_articulos una vez para evitar recargas constantes
if 'db_articulos' not in st.session_state:
    st.session_state.db_articulos = f.obtainTable('Articulos')

# df_display será el DataFrame que se mostrará.
# Por defecto, muestra toda la tabla al inicio o después de un reseteo.
if 'df_display_articulos' not in st.session_state:
    st.session_state.df_display_articulos = st.session_state.db_articulos.copy()

# --- FORMULARIO DE BÚSQUEDA ---
st.subheader('Buscar Artículos')
# Instanciamos ItemForm solo para búsqueda
formSearch = forms.ItemForm('search', 'Formulario de Búsqueda de Artículos', 'Buscar Artículo')

# Lógica para manejar el botón de búsqueda
if formSearch.Button:
    # Construir el diccionario de parámetros de búsqueda usando los valores del formulario
    # Los valores de formSearch.item y formSearch.desc ya reflejan el estado actual de los inputs
    search_params = {
        'Articulo': formSearch.item,
        'Descripcion': formSearch.desc,
    }
    
    # Aplicar la función de búsqueda sobre una copia del DataFrame original completo
    st.session_state.df_display_articulos = f.searchFunction(st.session_state.db_articulos.copy(), search_params)

    if st.session_state.df_display_articulos.empty:
        st.info("No se encontraron artículos con esos criterios de búsqueda.")

# Lógica para manejar el botón de reset del formulario de búsqueda
if formSearch.ButtonReset:
    # Al presionar el botón de reset, limpia los campos del formulario de búsqueda
    # y reinicia la tabla a su estado original (todos los artículos).
    st.session_state.df_display_articulos = st.session_state.db_articulos.copy()
    
    # Un st.rerun() ya está dentro de forms.py cuando se presiona el ButtonReset,
    # pero si queremos asegurar que la tabla se refresque con todos los datos aquí,
    # podríamos incluirlo, aunque el de forms.py ya debería bastar.
    # st.rerun() # Descomentar si el rerun en forms.py no refresca la tabla lo suficiente

st.markdown("---")

## **Visualización de Datos**

st.subheader('Resultados de Artículos')

if not st.session_state.df_display_articulos.empty:
    column_config = {
        "ID": st.column_config.NumberColumn("ID del Artículo", disabled=True),
        "Articulo": st.column_config.TextColumn("Artículo"),
        "Descripcion": st.column_config.TextColumn("Descripción"),
        "Coste_Material_Sugerido": st.column_config.NumberColumn("Coste Material", format="%.2f", disabled=True),
        "Coste_Proveedor_Sugerido": st.column_config.NumberColumn("Coste Proveedor", format="%.2f", disabled=True),
        "Importe_Sugerido": st.column_config.NumberColumn("Importe", format="%.2f", disabled=True),
    }
    
    # Mostramos la tabla, ahora con todos los campos deshabilitados para edición
    st.dataframe(st.session_state.df_display_articulos, column_config=column_config, hide_index=True)
else:
    st.info("No hay artículos para mostrar con los criterios actuales.")