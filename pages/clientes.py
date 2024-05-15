import streamlit as st
import pandas as pd 
import functions as f
import forms
import inspect

#title
st.markdown("# Clientes 👨‍🦰👩‍🦰")
st.sidebar.markdown("# Clientes 👨‍🦰👩‍🦰")

#table calculations
fileName = f.obtainPath('clientes')
db = pd.read_excel(fileName)
max_id, min_id = f.returnMaxMinID(db)

#table types 
phone_nos = db.Telefono.astype(str).replace('^(\d{3})(\d{2})(\d{2})(\d{2})$', r'\1 \2 \3 \4')
db.Telefono = phone_nos.where(db.Telefono.astype(str).str.contains('^\d{9}$'))

#column formats
col1, col2 = st.columns(2)

# form submit display
with col1:
    formSubmit = forms.CustomerForm('submit', 'Formulario para Insertar','Guardar registro')
    print(formSubmit.phone)

#form submit add
if formSubmit.Button:
    
    # new datasource
    new_row = {'ID': [max_id+1],
                'Nombre': [formSubmit.name], 
                'Telefono': [formSubmit.phone]}
    
    f.submitDatasource(new_row, fileName, 'Nombre')

# form search display
with col2:
    formSearch = forms.CustomerForm('search','Formulario para Buscar','Buscar registro')

# form search filter
if formSearch.Button:
    db = f.searchFunction(db, formSearch, "Nombre", "Telefono")

#table display
f.displayTable(db)

# delete form
f.deleteForm(min_id, max_id, fileName)