import streamlit as st
import pandas as pd 
import functions as f
import forms

#title
st.markdown("# Articulos 📦")
st.sidebar.markdown("# Articulos 📦")

#table calculations
fileName = f.obtainPath('articulos')
db = f.obtainTable('articulos')
max_id, min_id = f.returnMaxMinID(db)

#column formats
col1, col2 = st.columns(2)

#form submit display
with col1:
    formSubmit = forms.ItemForm('submit', 'Formulario para Insertar','Guardar registro')

if formSubmit.Button:

    # new datasource
    new_row = {'ID': [max_id+1],
                'Articulo': [formSubmit.item], 
                'Descripción': [formSubmit.desc], 
                'Coste Sugerido': [formSubmit.cost], 
                'Precio Sugerido': [formSubmit.price] }
    
    f.submitDatasource(new_row, fileName, uniqueColumn='Articulo')

# form search display
with col2:
    formSearch = forms.ItemForm('search','Formulario para Buscar','Buscar registro')

# form search filter
if formSearch.Button:
    db = f.searchFunction(db, formSearch, "Articulo", "Descripción")

#table display
f.displayTable(db)

# delete form
f.deleteForm(min_id, max_id, fileName)
