import streamlit as st
import pandas as pd 
import functions as f
import forms

#define parameters

#title
st.markdown("# Clientes 👨‍🦰👩‍🦰")
st.sidebar.markdown("# Clientes 👨‍🦰👩‍🦰")

#table calculations
fileName = f.obtainPath('clientes')
db = pd.read_excel(fileName)
max_id, min_id = f.returnMaxMinID(db)

#table format 
db["Telefono"] = db["Telefono"].astype(str)


#column formats
col1, col2 = st.columns(2)

# form display
with col1:
    formSubmit = forms.CustomerForm('submit', 'Formulario para Insertar','Guardar registro')

if formSubmit.Button:
    
    # new datasource
    new_row = {'ID': [max_id+1],
                'Nombre': [formSubmit.name], 
                'Telefono': [formSubmit.phone]}
    
    f.submitDatasource(new_row, fileName, 'Nombre')

# form search display
with col2:
    formSearch = forms.CustomerForm('search','Formulario para Buscar','Buscar registro')

searchVariables = formSearch.name + formSearch.phone
if formSearch.Button and searchVariables not in (' '):
    if formSearch.name not in (' '): 
        db = db.loc[db["Nombre"] == formSearch.name]
    if formSearch.phone not in (' '): 
        db = db.loc[db["Telefono"] == formSearch.phone]

print(db)
print(formSearch.name)
print('name', 'b', formSearch.name, 'a')

# delete form
f.deleteForm(min_id, max_id, fileName)

#table display
#st.dataframe(db, hide_index=True, use_container_width=True)
f.displayTable(db)