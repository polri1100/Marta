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
                        page_icon='📖')
st.markdown("# Pedidos 📖")
st.sidebar.markdown("# Pedidos 📖")

# Load databases
db_pedidos = f.obtainTable('Pedidos')
db_articulos = f.obtainTable('Articulos')
db_clientes = f.obtainTable('Clientes')

#Join Databases
db_joined = f.ordersJoin(db_pedidos, db_clientes, db_articulos)
#table calculations
list_items = db_articulos['Articulo'].unique().tolist() if not db_articulos.empty and 'Articulo' in db_articulos.columns else []
list_customers = db_clientes['Nombre'].unique().tolist() if not db_clientes.empty and 'Nombre' in db_clientes.columns else []
max_id, min_id = f.returnMaxMinID(db_pedidos)

#column formats
col1, col2 = st.columns((2,1))

# form submit display
with col1:
    formSubmit = forms.OrderForm('submit', 'Formulario para Insertar','Guardar registro', list_items, list_customers, db_articulos)

if formSubmit.Button:
    # IDs detection: (esto está bien, pero podría fallar si formSubmit.customer/item no se encuentran)
    # Es buena práctica añadir un try-except o una comprobación.
    try:
        customer_id = int(db_clientes.loc[db_clientes['Nombre'] == formSubmit.customer, 'ID'].values[0])
        item_id = int(db_articulos.loc[db_articulos['Articulo'] == formSubmit.item, 'ID'].values[0])
    except IndexError:
        st.error("Error: Cliente o Artículo no encontrado. Por favor, selecciona uno válido de las listas.")
        st.stop() # Detiene la ejecución para que el usuario corrija

    # new datasource - IMPORTANTE: NO INCLUIR 'ID' SI ES IDENTITY EN SUPABASE
    new_row_data = {
        'Cliente_id': customer_id,
        'Articulo_id': item_id,
        'Descripcion': formSubmit.desc,
        # Convertir fechas a formato ISO 8601 string. Supabase lo prefiere para DATE/TIMESTAMP
        'Fecha_Entrega': formSubmit.deliveryDate.isoformat() if formSubmit.deliveryDate else None,
        'Cantidad': int(formSubmit.quantity), # Asegurar que es int de Python
        'Coste': float(formSubmit.cost),     # Asegurar que es float de Python
        'Precio': float(formSubmit.price),   # Asegurar que es float de Python
        'Pagado': bool(formSubmit.payed),    # Asegurar que es bool de Python
        'Fecha_Recogida': formSubmit.pickUpDate.isoformat() if formSubmit.pickUpDate else None
    }
    
    f.submitDatasource(new_row_data, 'Pedidos') 
    

# form search display
with col2:
    formSearch = forms.OrderForm('search','Formulario para Buscar','Buscar registro')

db_display = db_joined.copy() # Inicializar siempre con la tabla completa
# form search filter
if formSearch.Button:
    db_joined = f.searchFunction(db_joined.copy(), formSearch, "Fecha_Entrega", "Nombre", "Articulo", "Descripcion", "Fecha_Recogida", "Pagado")

# Lógica para el botón de reseteo de búsqueda
if formSearch.ButtonReset:
    st.rerun()

st.subheader("Visualización y Edición de Pedidos")

if not db_joined.empty:
    if 'Pagado' in db_joined.columns:
        db_joined['Pagado'] = db_joined['Pagado'].astype(bool)
    for col_date in ['Fecha_Entrega', 'Fecha_Recogida']: # Usa nombres exactos de columnas
        if col_date in db_joined.columns:
            db_joined[col_date] = pd.to_datetime(db_joined[col_date], errors='coerce')

edited_db_joined = st.data_editor(
    db_joined, # Le pasamos el DataFrame actual (filtrado o completo)
    hide_index=True,
    use_container_width=True,
    key="pedidos_data_editor" # Un identificador único para este widget
)

if st.button("Guardar Cambios en Pedidos"):
    original_db_pedidos = f.obtainTable('Pedidos')
    
    if 'ID' in original_db_pedidos.columns:
        original_db_pedidos['ID'] = original_db_pedidos['ID'].astype(str)
    if 'ID' in edited_db_joined.columns:
        edited_db_joined['ID'] = edited_db_joined['ID'].astype(str)
        
    # Mapear de nuevo Nombre a Cliente_id y Articulo a Articulo_id si se perdieron
    if 'Nombre' in edited_db_joined.columns and 'Cliente_id' not in edited_db_joined.columns:
        name_to_customer_id = db_clientes.set_index('Nombre')['ID'].to_dict()
        edited_db_joined['Cliente_id'] = edited_db_joined['Nombre'].map(name_to_customer_id)
    
    if 'Articulo' in edited_db_joined.columns and 'Articulo_id' not in edited_db_joined.columns:
        item_to_article_id = db_articulos.set_index('Articulo')['ID'].to_dict()
        edited_db_joined['Articulo_id'] = edited_db_joined['Articulo'].map(item_to_article_id)

    pedido_cols_for_update = [
        'ID', 'Cliente_id', 'Articulo_id', 'Descripcion', 'Fecha_Entrega',
        'Cantidad', 'Coste', 'Precio', 'Pagado', 'Fecha_Recogida'
    ]

    df_pedidos_to_compare = edited_db_joined[pedido_cols_for_update].copy()
    
    if 'Pagado' in df_pedidos_to_compare.columns:
        df_pedidos_to_compare['Pagado'] = df_pedidos_to_compare['Pagado'].astype(bool)
    for col_date in ['Fecha_Entrega', 'Fecha_Recogida']:
        if col_date in df_pedidos_to_compare.columns:
            df_pedidos_to_compare[col_date] = pd.to_datetime(df_pedidos_to_compare[col_date], errors='coerce')

    merged_df = pd.merge(df_pedidos_to_compare, original_db_pedidos, on='ID', how='left', suffixes=('_edited', '_original'))

    updated_rows_data = []

    for index, row in merged_df.iterrows():
        record_id = row['ID']
        is_changed = False
        data_for_update = {}
        
        for col in pedido_cols_for_update:
            if col == 'ID':
                continue
            
            edited_val = row.get(f'{col}_edited')
            original_val = row.get(f'{col}_original')

            # Manejo especial para booleanos
            if col == 'Pagado':
                edited_val = bool(edited_val) if pd.notna(edited_val) else False
                original_val = bool(original_val) if pd.notna(original_val) else False
            # Manejo especial para fechas (comparar solo la parte de la fecha si es necesario)
            elif col in ['Fecha_Entrega', 'Fecha_Recogida']:
                # Convertir a datetime para una comparación robusta
                edited_date = pd.to_datetime(edited_val, errors='coerce') if pd.notna(edited_val) else None
                original_date = pd.to_datetime(original_val, errors='coerce') if pd.notna(original_val) else None

                if (edited_date is None and original_date is not None) or \
                    (edited_date is not None and original_date is None) or \
                    (edited_date is not None and original_date is not None and edited_date.date() != original_date.date()):
                    is_changed = True
                    data_for_update[col] = edited_date.isoformat() if edited_date else None
                continue
            
            # Asegurar que los valores numéricos son tipos nativos de Python
            if col in ['Cantidad', 'Coste', 'Precio']:
                edited_val = int(edited_val) if col == 'Cantidad' and pd.notna(edited_val) else (float(edited_val) if pd.notna(edited_val) else 0)
                original_val = int(original_val) if col == 'Cantidad' and pd.notna(original_val) else (float(original_val) if pd.notna(original_val) else 0)


            if str(edited_val) != str(original_val):
                is_changed = True
                data_for_update[col] = edited_val
        
        if is_changed:
            updated_rows_data.append({'ID': record_id, 'data': data_for_update})

    if updated_rows_data:
        for item in updated_rows_data:
            record_id = item['ID']
            data_to_update = item['data']
            
            if data_to_update:
                f.update_record('Pedidos', record_id, data_to_update, id_column_name='ID')
        
        st.rerun()
    else:
        st.info("No hay cambios para guardar.")


# delete form
max_id, min_id = f.returnMaxMinID(db_pedidos)
f.deleteForm(min_id, max_id, 'Pedidos')