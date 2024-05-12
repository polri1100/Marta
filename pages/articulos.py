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

#table display
st.dataframe(db, hide_index=True, use_container_width=True)

#form formats
col1, col2 = st.columns(2)


# param_dict = {'item': ['Articulo', 'text'],
#               'desc': ['Descripción', 'text'],
#               'cost': ['Coste Sugerido', 'number'],
#               'price': ['Precio Sugerido', 'number']}

# # form submit display
# d, submitButton1 = f.createForm('submit', "Formulario para Insertar", param_dict)
# d

#form submit display
with col1:
    form1 = forms.Form('Formulario para Insertar')
    # with st.form(key='item-form-submit'):
    #     st.write("Formulario para Insertar")
    #     item = st.text_input('Articulo')
    #     desc = st.text_input('Descripción')
    #     cost = st.number_input('Coste Sugerido')
    #     price = st.number_input('Precio Sugerido')

    #submitButton = form1.submitButton

if form1.submitButton:

    # new datasource
    new_row = {'ID': [max_id+1],
                'Articulo': [form1.item], 
                'Descripción': [form1.desc], 
                'Coste Sugerido': [form1.cost], 
                'Precio Sugerido': [form1.price] }
    
    f.submitDatasource(new_row, fileName, 'Articulo')

# form search display
with col2:
    with st.form(key='item-form-search'):
        st.write("Formulario para Buscar")
        item = st.text_input('Articulo')
        desc = st.text_input('Descripción')
        cost = st.number_input('Coste Sugerido')
        price = st.number_input('Precio Sugerido')

        searchButton = st.form_submit_button('Buscar registro')


# delete form
f.deleteForm(min_id, max_id, fileName)
