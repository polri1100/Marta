import streamlit as st
import functions as f
import forms

#Define Variables
# if 'payedToggle' not in st.session_state:
#     st.session_state.payedToggle = False

#title
st.set_page_config(layout="wide",
                       page_title='Pedidos',
                       page_icon='👚')
st.markdown("# Pedidos 📖")
st.sidebar.markdown("# Pedidos 📖")

# Load databases
db_pedidos = f.obtainTable('pedidos')
db_articulos = f.obtainTable('articulos')
db_clientes = f.obtainTable('clientes')

#Join Databases
db_joined = f.ordersJoin(db_pedidos, db_clientes, db_articulos)

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
    
    db_joined = f.submitDatasource(newRow=new_row, fileName='pedidos')
   
    #per a tornar a tenir la taula amb els unics camps que volem
    db_pedidos = f.obtainTable('pedidos')
    db_joined = f.ordersJoin(db_pedidos, db_clientes, db_articulos)


# form search display
with col2:
    formSearch = forms.OrderForm('search','Formulario para Buscar','Buscar registro')

# form search filter
if formSearch.Button:
    db_joined = f.searchFunction(db_joined, formSearch, "Fecha Entrega", "Nombre", "Articulo", "Descripcion", "Fecha Recogida", "Pagado")

#table display
f.displayTable(db_joined, 'ID')

# delete form
# We asign again to update the max_id in the form
max_id, min_id = f.returnMaxMinID(db_pedidos)
f.deleteForm(min_id, max_id, 'pedidos')
