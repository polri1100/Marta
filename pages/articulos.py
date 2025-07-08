import streamlit as st
import functions as f
import forms
import pandas as pd

#title
st.set_page_config(layout="wide",
                       page_title='Articulos',
                       page_icon='📦')
st.markdown("# Articulos 📦")
st.sidebar.markdown("# Articulos 📦")

#table calculations
db = f.obtainTable('Articulos')
max_id, min_id = f.returnMaxMinID(db)

#column formats
col1, col2 = st.columns(2)

#form submit display
with col1:
    formSubmit = forms.ItemForm('submit', 'Formulario para Insertar','Guardar registro')

if formSubmit.Button:

    # new datasource
    new_article_data = {
        'Articulo': formSubmit.item,
        'Descripcion': formSubmit.desc, # Asegúrate que tu columna en Supabase es 'Descripcion'
        'Coste_Sugerido': formSubmit.cost, # Asegúrate que tu columna en Supabase es 'Coste_Sugerido'
        'Precio_Sugerido': formSubmit.price # Asegúrate que tu columna en Supabase es 'Precio_Sugerido'
    }

    f.submitDatasource(new_article_data, 'Articulos', uniqueColumn='Articulo')

# form search display
with col2:
    formSearch = forms.ItemForm('search','Formulario para Buscar','Buscar registro')

# form search filter
if formSearch.Button:
    db = f.searchFunction(db, formSearch, "Articulo", "Descripcion") # Asegúrate que es "Descripcion" en tu DB
elif formSearch.ButtonReset: # Manejar el botón de reset
    db = f.obtainTable('Articulos') # Recargar la tabla original


#table display
f.displayTable(db, 'ID')

# --- Formulario para Eliminar Artículos ---
# Volver a calcular max_id/min_id por si se insertó/eliminó algo
db_for_delete_form = f.obtainTable('Articulos') # Opcional, para asegurar IDs actualizados
max_id, min_id = f.returnMaxMinID(db_for_delete_form)
f.deleteForm(min_id, max_id, 'Articulos') # Pasa el nombre de la tabla de Supabase

