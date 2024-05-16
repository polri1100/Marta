import streamlit as st
import pandas as pd 
import functions as f
import forms

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
                       'Articulo', 'Descripcion_x',
                       'Cantidad', 'Coste', 'Precio',
                       'Pagado', 'Fecha Recogida']]

db_joined["Pagado"] = db_joined["Pagado"].astype('bool')
db_joined["Fecha Entrega"] = db_joined["Fecha Entrega"].dt.strftime('%d/%m/%Y')
db_joined["Fecha Recogida"] = db_joined["Fecha Recogida"].dt.strftime('%d/%m/%Y')

db_joined.rename(columns={'ID_x': 'ID'}, inplace=True)
db_joined.rename(columns={'Descripcion_x': 'Descripcion'}, inplace=True)

db_joined = db_joined.sort_values(by=['ID'], ascending=False)

#table calculations
list_items = db_articulos['Articulo'].unique()
list_customers = db_clientes['Nombre'].unique()
max_id, min_id = f.returnMaxMinID(db_pedidos)

#column formats
col1, col2 = st.columns((2,1))

# form submit display
with col1:
    formSubmit = forms.OrderForm('submit', 'Formulario para Insertar','Guardar registro', list_items, list_customers, db_articulos)

if formSubmit.Button:

    #ids detection:
    customer_id = db_clientes.loc[db_clientes['Nombre'] == formSubmit.customer, 'ID'].values[0]
    item_id = db_articulos.loc[db_articulos['Articulo'] == formSubmit.item, 'ID'].values[0]

    # new datasource
    new_row = {'ID': [max_id+1],
                'Cliente_id': [customer_id], 
                'Articulo_id': [item_id], 
                'Descripcion': [formSubmit.desc],
                'Fecha Entrega': [formSubmit.deliveryDate], 
                'Cantidad': [formSubmit.quantity],
                'Coste': [formSubmit.cost],
                'Precio': [formSubmit.price],
                'Pagado': [formSubmit.payed],
                'Fecha Recogida': [formSubmit.pickUpDate]}
    
    f.submitDatasource(new_row, fileName)

    # db_pedidos = f.obtainTable('pedidos')

# form search display
with col2:
    formSearch = forms.OrderForm('search','Formulario para Buscar','Buscar registro')

# form search filter
if formSearch.Button:
    db_joined = f.searchFunction(db_joined, formSearch, "Fecha Entrega", "Nombre", "Articulo", "Descripcion", "Fecha Recogida", "Pagado")

#table display
f.displayTable(db_joined)

# delete form
f.deleteForm(min_id, max_id, fileName)
