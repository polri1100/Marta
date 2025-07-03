import streamlit as st
import functions as f
import forms
import pandas as pd

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
    db_joined = f.searchFunction(db_joined.copy(), formSearch, "Fecha Entrega", "Nombre", "Articulo", "Descripcion", "Fecha Recogida", "Pagado")

st.subheader("Visualización y Edición de Pedidos")
edited_db_joined = st.data_editor(
    db_joined, # Le pasamos el DataFrame actual (filtrado o completo)
    hide_index=True,
    use_container_width=True,
    key="pedidos_data_editor" # Un identificador único para este widget
)

if st.button("Guardar Cambios en Pedidos"):
    for col_date in ['Fecha Entrega', 'Fecha Recogida']:
        if col_date in edited_db_joined.columns:
            # Convierte al formato deseado para Google Sheets si pygsheets lo espera de una manera específica,
            # o simplemente a datetime para que pygsheets lo maneje.
            edited_db_joined[col_date] = pd.to_datetime(edited_db_joined[col_date], errors='coerce').dt.strftime('%Y-%m-%d')
            # 'errors='coerce' convertirá fechas no válidas en NaT (Not a Time)
            # .dt.strftime('%Y-%m-%d') para asegurar un formato consistente de string si lo necesitas,
            # aunque pygsheets suele manejar objetos datetime directamente.

    # Aquí es crucial volver al formato de la tabla 'pedidos' original para guardar
    # db_joined es el resultado de un merge. Necesitamos extraer solo las columnas de 'pedidos'
    # para guardarlas de nuevo en la hoja 'pedidos'.
    
    # Creamos un DataFrame con solo las columnas que pertenecen a la hoja 'pedidos'
    # Asegúrate de que los nombres de las columnas coincidan con los de tu Google Sheet 'pedidos'
    # Y que los tipos de datos sean compatibles antes de subir.
    
    # Define las columnas que esperas en tu hoja 'pedidos' en Google Sheets
    # Ajusta esto para que coincida exactamente con los nombres de tus columnas en la hoja 'pedidos'
    # y el orden en el que pygsheets espera los datos.
    
    # ATENCIÓN: La columna 'Pagado' en tu 'ordersJoin' se mapea a booleano,
    # pero para guardar en Google Sheets, a menudo es mejor que sea "TRUE" o "FALSE" string,
    # o 1/0, dependiendo de cómo manejes los booleanos en Sheets.
    # Asumo que la columna 'Pagado' en la hoja de Google Sheets 'pedidos' es "TRUE" o "FALSE" como string.
    
    # Paso 1: Reconstruir el DataFrame 'db_pedidos' a partir de 'edited_db_joined'
    # Esto es vital porque 'edited_db_joined' tiene columnas de clientes y artículos que no van en 'pedidos'.
    df_pedidos_to_save = edited_db_joined[[
        'ID',
        'Fecha Entrega', # Esta columna viene del formulario directamente, o se deriva
        'Cantidad',
        'Coste',
        'Precio',
        'Pagado',
        'Fecha Recogida',
        'Descripcion',
        # Recuperar Cliente_id y Articulo_id a partir de los nombres
        # Esto requiere mapear de nuevo desde 'Nombre' a 'Cliente_id' y 'Articulo' a 'Articulo_id'
        # o asegurarte de que estas IDs están presentes y no se pierden en el editor
    ]].copy()

    # Re-mapear Nombres a IDs si no están directamente presentes en edited_db_joined
    # Esto es crucial si el usuario solo ve "Nombre" y "Articulo" en la tabla editada
    # y no las IDs subyacentes.
    # Asumo que 'Cliente_id' y 'Articulo_id' son parte del DataFrame 'edited_db_joined'
    # si se necesitan para la hoja 'pedidos'. Si no, tendrás que recalcularlas.

    # Para el ejemplo, asumo que las IDs están presentes en edited_db_joined o que se pueden obtener.
    # Si 'Cliente_id' y 'Articulo_id' no están directamente en edited_db_joined,
    # y solo tienes 'Nombre' y 'Articulo', necesitarás el siguiente paso para recuperarlas:

    # Mapear 'Nombre' a 'Cliente_id'
    name_to_customer_id = db_clientes.set_index('Nombre')['ID'].to_dict()
    df_pedidos_to_save['Cliente_id'] = edited_db_joined['Nombre'].map(name_to_customer_id)

    # Mapear 'Articulo' a 'Articulo_id'
    item_to_article_id = db_articulos.set_index('Articulo')['ID'].to_dict()
    df_pedidos_to_save['Articulo_id'] = edited_db_joined['Articulo'].map(item_to_article_id)
    
    # Asegúrate de que 'Descripcion' en la hoja 'pedidos' es el 'Descripcion' original del pedido,
    # no 'Descripcion_x' de la tabla unida.
    # Asumo que 'Descripcion' es una columna directamente editable en el data_editor y corresponde
    # a la columna 'Descripcion' en tu hoja de 'pedidos'.

    # Asegurarse de que la columna 'Pagado' se guarde como "TRUE"/"FALSE" strings si así lo espera la hoja de Google Sheets
    df_pedidos_to_save['Pagado'] = df_pedidos_to_save['Pagado'].map({True: "TRUE", False: "FALSE"})

    # Renombrar columnas si es necesario para que coincidan con la hoja de Google Sheets 'pedidos'
    # Por ejemplo, si en la hoja original de 'pedidos' tienes 'Descripcion' y no 'Descripcion_x'
    # df_pedidos_to_save.rename(columns={'Descripcion_x': 'Descripcion'}, inplace=True) # Solo si edited_db_joined aún tiene _x
    
    # La columna 'Descripcion' que se edita en la interfaz es la misma que va a la hoja 'pedidos'.
    # df_pedidos_to_save['Descripcion'] = edited_db_joined['Descripcion'] # Asumiendo que el editor devuelve 'Descripcion'

    # Finalizar la selección de columnas para la subida
    # Asegúrate de que este orden y nombres de columnas coincidan EXACTAMENTE con tu hoja 'pedidos'
    df_pedidos_final = df_pedidos_to_save[[
        'ID',
        'Cliente_id',
        'Articulo_id',
        'Descripcion', # Asegúrate de que esta columna esté correctamente manejada
        'Fecha Entrega',
        'Cantidad',
        'Coste',
        'Precio',
        'Pagado',
        'Fecha Recogida'
    ]]
    
    # Llamar a la función save_data
    f.save_data(df_pedidos_final, 'pedidos')
    



# delete form
# We asign again to update the max_id in the form
max_id, min_id = f.returnMaxMinID(db_pedidos)
f.deleteForm(min_id, max_id, 'pedidos')
