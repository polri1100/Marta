import streamlit as st
import pandas as pd 
import functions as f
from datetime import datetime

#Define Variables
# if 'payedToggle' not in st.session_state:
#     st.session_state.payedToggle = False

#title
st.markdown("# Pedidos 📖")
st.sidebar.markdown("# Pedidos 📖")

# Load databases
fileName = f.obtainPath('pedidos')
db_pedidos = f.obtainTable('pedidos')
db_articulos = f.obtainTable('articulos')
db_clientes = f.obtainTable('clientes')

#Join Databases
db_joined = db_pedidos.merge(db_clientes, left_on='Cliente_id', right_on='ID', how='left')
db_joined = db_joined.merge(db_articulos, left_on='Articulo_id', right_on='ID', how='left')
db_joined = db_joined[['ID_x', 'Fecha Entrega', 
                       'Nombre',
                       'Articulo', 'Descripción', 
                       'Cantidad', 'Coste', 'Precio',
                       'Pagado', 'Fecha Recogida']]

db_joined["Pagado"] = db_joined["Pagado"].astype('bool')
db_joined["Fecha Entrega"] = db_joined["Fecha Entrega"].dt.strftime('%d/%m/%Y')
db_joined["Fecha Recogida"] = db_joined["Fecha Recogida"].dt.strftime('%d/%m/%Y')

db_joined.rename(columns={'ID_x': 'ID'}, inplace=True)

db_joined = db_joined.sort_values(by=['ID'], ascending=False)

#table display
st.dataframe(db_joined, hide_index=True, use_container_width=True)

#table calculations
list_items = db_articulos['Articulo'].unique()
list_customers = db_clientes['Nombre'].unique()
max_id, min_id = f.returnMaxMinID(db_pedidos)


# form submit display
with st.form(key='item-form-submit'):
    st.write("Formulario para Insertar")

    item = st.selectbox('Articulo', (list_items))
    customer = st.selectbox('Cliente', (list_customers))
    deliveryDate = st.date_input('Fecha Entrega', format="DD/MM/YYYY")
    quantity = st.number_input('Cantidad', step=1)
    suggestedButton = st.form_submit_button('Ver coste y precio sugeridos')

    if suggestedButton:

        cost = st.number_input('Coste', db_articulos.loc[db_articulos['Articulo'] == item, 'Coste Sugerido'].iat[0])
        price = st.number_input('Precio', db_articulos.loc[db_articulos['Articulo'] == item, 'Precio Sugerido'].iat[0])

    else:
        cost = st.number_input('Coste', value = 0)
        price = st.number_input('Precio', value = 0)

    payed = st.selectbox('Pagado?', ('Pagado', 'No pagado'))
    
    if payed == 'Pagado':
        payed = True
    else:
        payed = False
    
    pickUpDate = st.date_input('Fecha Recogida', None, format="DD/MM/YYYY")
    submitButton = st.form_submit_button('Guardar registro')


if submitButton:

    #ids detection:
    customer_id = db_clientes.loc[db_clientes['Nombre'] == customer, 'ID'][0]
    item_id = db_articulos.loc[db_articulos['Articulo'] == item, 'ID'][0]

    # new datasource
    new_row = {'ID': [max_id+1],
                'Cliente_id': [customer_id], 
                'Articulo_id': [item_id], 
                'Fecha Entrega': [deliveryDate], 
                'Cantidad': [quantity],
                'Coste': [cost],
                'Precio': [price],
                'Pagado': [payed],
                'Fecha Recogida': [pickUpDate]}
    
    f.submitDatasource(new_row, fileName)

    db_pedidos = f.obtainTable('pedidos')


# delete form
f.deleteForm(min_id, max_id, fileName)
