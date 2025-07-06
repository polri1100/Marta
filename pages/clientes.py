import streamlit as st
import functions as f
import forms
import pandas as pd


#title
st.set_page_config(layout="wide",
                        page_title='Clientes',
                        page_icon='👚')
st.markdown("# Clientes 👨‍🦰👩‍🦰")
st.sidebar.markdown("# Clientes 👨‍🦰👩‍🦰")

#table calculations
db_clientes = f.obtainTable('clientes')
max_id, min_id = f.returnMaxMinID(db_clientes)

#table types 
# phone_nos = db.Telefono.astype(str).replace('^(\d{3})(\d{2})(\d{2})(\d{2})$', r'\1 \2 \3 \4')
# db.Telefono = phone_nos.where(db.Telefono.astype(str).str.contains('^\d{9}$'))

#column formats
col1, col2 = st.columns(2)

# form submit display
with col1:
    formSubmit = forms.CustomerForm('submit', 'Formulario para Insertar','Guardar registro')

#form submit add
if formSubmit.Button:
    
    # new datasource
    new_row = {'ID': [max_id+1],
                'Nombre': [formSubmit.name],
                'Descripcion': [formSubmit.desc], 
                'Telefono': [formSubmit.phone]}
    
    db_clientes = f.submitDatasource(new_row, 'clientes', uniqueColumn='Nombre', restrictedValue=formSubmit.phone)
    max_id, min_id = f.returnMaxMinID(db_clientes)


# form search display
with col2:
    formSearch = forms.CustomerForm('search','Formulario para Buscar','Buscar registro')

    db_display=db_clientes.copy()
# form search filter
if formSearch.Button:
    db_display = f.searchFunction(db_clientes.copy(), formSearch, "Nombre", "Descripcion", "Telefono")

#table display
st.subheader("Visualización y Edición de Clientes")

db_clientes['Telefono'] = db_clientes['Telefono'].astype(str)
edited_db_clientes = st.data_editor(
    db_display, # Pasamos el DataFrame que puede estar filtrado
    hide_index=True,
    use_container_width=True,
    key="clientes_data_editor" # Identificador único
)

if st.button("Guardar Cambios en Clientes"):
    # Asegurarse de que el teléfono sigue siendo un string, ya que st.data_editor podría cambiarlo.
    edited_db_clientes['Telefono'] = edited_db_clientes['Telefono'].astype(str)

    if not all(edited_db_clientes['Telefono'].str.match(r'^\d{9}$')):
        st.error("Error: Todos los números de teléfono deben tener 9 dígitos.")
        st.stop() # Detiene la ejecución para que el usuario corrija.
    
    f.save_data(edited_db_clientes, 'clientes')


# delete form
# We asign again to update the max_id in the form
max_id, min_id = f.returnMaxMinID(db_clientes)
f.deleteForm(min_id, max_id, 'clientes')