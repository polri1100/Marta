import streamlit as st
import pandas as pd 
import functions as f

#title
st.markdown("# Clientes 👨‍🦰👩‍🦰")
st.sidebar.markdown("# Clientes 👨‍🦰👩‍🦰")

#table calculations
fileName = f.obtainPath('clientes')
db = pd.read_excel(fileName)
max_id, min_id = f.returnMaxMinID(db)

#table format 
db["Telefono"] = db["Telefono"].astype(str)

#table display
st.dataframe(db, hide_index=True, use_container_width=True)

# form display
with st.form(key='item-form-submit'):
    st.write("Formulario para Insertar")
    name = st.text_input('Nombre')
    #surname = form.text_input('Apellido')
    #aka = form.text_input('Apodo')
    phone = st.text_input('Telefono')

    submit = st.form_submit_button('Guardar registro')

if submit:
    
    # new datasource
    new_row = {'ID': [max_id+1],
                'Nombre': [name], 
                #'Apellido': [surname], 
                #'Apodo': [aka], 
                'Telefono': [phone] }
    
    f.submitDatasource(new_row, fileName, 'Nombre')

# delete form
f.deleteForm(min_id, max_id, fileName)
