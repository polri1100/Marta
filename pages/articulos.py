import streamlit as st
import functions as f
import forms
import pandas as pd
import time
#title
st.set_page_config(layout="wide",
                       page_title='Articulos',
                       page_icon='📦')
st.markdown("# Articulos 📦")
st.sidebar.markdown("# Articulos 📦")

# Cargar la base de datos de Artículos
db_articulos = f.obtainTable('Articulos')

# --- SECCIÓN DE BÚSQUEDA (CENTRADO Y MÁS GRANDE) ---

# Usar un contenedor para el formulario centrado
st.markdown("<h3 style='text-align: center;'>Buscar Artículos</h3>", unsafe_allow_html=True)

# Un truco para centrar y dar más "ancho" aparente al formulario
# Usamos columnas vacías a los lados. Ajusta el 1 y el 3 para el ancho.
col_left_spacer, col_form, col_right_spacer = st.columns([1, 3, 1])

with col_form:
    # Crear una instancia del ItemForm en modo 'search'
    formSearch = forms.ItemForm('search', '', 'Buscar') # El título del formulario ya lo pusimos con el h3

    # Inicializar df_display con la tabla completa por defecto
    df_display = db_articulos.copy()
    
    # Lógica para manejar el botón de búsqueda
    if formSearch.Button:
        # Recuperar los valores de búsqueda de session_state
        search_params = {
            'Articulo': st.session_state.get('item_search_articulo_value', ''),
            'Descripcion': st.session_state.get('item_search_descripcion_value', '')
        }
        
        # Filtrar el DataFrame basado en los parámetros de búsqueda
        df_display = f.searchFunction(db_articulos.copy(), search_params, allowed_columns=['Articulo', 'Descripcion'])
        
        if df_display.empty:
            st.info("No se encontraron artículos con esos criterios de búsqueda.")
    
    # Lógica para manejar el botón de reset de búsqueda
    if formSearch.ButtonReset:
        # Limpiar los valores de búsqueda en session_state
        st.session_state[f'item_search_articulo_value'] = ''
        st.session_state[f'item_search_descripcion_value'] = ''
        st.rerun() # Recargar la página para limpiar los campos y mostrar la tabla completa


# --- SECCIÓN DE VISUALIZACIÓN DE DATOS (CATÁLOGO COMPLETO O RESULTADOS DE BÚSQUEDA) ---

st.markdown("---") # Una línea divisoria para separar el formulario de la tabla
st.subheader('Catálogo de Artículos')

if not df_display.empty: # Usamos df_display que ya contiene los resultados de la búsqueda o el catálogo completo
    column_config = {
        "ID": st.column_config.NumberColumn("ID", disabled=True),
        "Articulo": st.column_config.TextColumn("Artículo"),
        "Descripcion": st.column_config.TextColumn("Descripción"),
        "Coste_Material_Sugerido": st.column_config.NumberColumn("Coste Material Sugerido", format="%.2f", step=0.01),
        "Coste_Proveedor_Sugerido": st.column_config.NumberColumn("Coste Proveedor Sugerido", format="%.2f", step=0.01),
        "Importe_Sugerido": st.column_config.NumberColumn("Importe Sugerido", format="%.2f", step=0.01),
    }
    
    # Usar st.dataframe para una vista de solo lectura
    st.dataframe(df_display, use_container_width=True, hide_index=True, column_config=column_config)
else:
    # Este mensaje solo se mostrará si df_display está vacío después de una búsqueda
    # O si db_articulos está vacío inicialmente (lo cual ya maneja la línea anterior)
    if formSearch.Button: # Solo muestra el "No hay artículos" si se hizo una búsqueda y no se encontró nada
        pass # El info de arriba ya lo manejará
    else: # Si db_articulos estaba vacío desde el principio
        st.info("No hay artículos para mostrar en el catálogo.")