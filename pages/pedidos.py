import streamlit as st
import functions as f
import forms
import pandas as pd
import time
import datetime
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

# Join Databases
db_joined = f.ordersJoin(db_pedidos, db_clientes, db_articulos)

if 'Cliente_id' in db_joined.columns:
    db_joined = db_joined.drop(columns=['Cliente_id'])
if 'Articulo_id' in db_joined.columns:
    db_joined = db_joined.drop(columns=['Articulo_id'])

# table calculations
list_items = db_articulos['Articulo'].unique().tolist() if not db_articulos.empty and 'Articulo' in db_articulos.columns else []
list_customers = db_clientes['Nombre'].unique().tolist() if not db_clientes.empty and 'Nombre' in db_clientes.columns else []
max_id, min_id = f.returnMaxMinID(db_pedidos)

# Columnas para organizar la interfaz
col1, col2 = st.columns((2,1))
    
# Formulario de inserción
with col1:
    st.subheader('Nuevo Pedido')
    # db_articulos se pasa a OrderForm para que pueda acceder a los costes sugeridos.
    formSubmit = forms.OrderForm('submit', 'Formulario para Insertar', 'Guardar registro', list_items, list_customers, db_articulos)

    if formSubmit.Button:
        cliente_id = None
        if st.session_state.customer_selectbox_key and not db_clientes.empty:
            filtered_cliente = db_clientes[db_clientes['Nombre'] == st.session_state.customer_selectbox_key]
            if not filtered_cliente.empty:
                cliente_id = int(filtered_cliente['ID'].iloc[0])

        articulo_id = None
        articulo_coste_material = 0.0
        articulo_coste_proveedor = 0.0
        articulo_importe = 0.0

        if st.session_state.item_selectbox_key and not db_articulos.empty:
            # Asegúrate de que la columna 'Articulo' en db_articulos es del tipo correcto para la comparación
            filtered_articulo = db_articulos[db_articulos['Articulo'].astype(str) == st.session_state.item_selectbox_key]
            if not filtered_articulo.empty:
                articulo_id = int(filtered_articulo['ID'].iloc[0])
                # Obtener los precios sugeridos directamente del DataFrame de artículos
                if 'Coste_Material_Sugerido' in filtered_articulo.columns:
                    articulo_coste_material = float(filtered_articulo['Coste_Material_Sugerido'].iloc[0])
                if 'Coste_Proveedor_Sugerido' in filtered_articulo.columns:
                    articulo_coste_proveedor = float(filtered_articulo['Coste_Proveedor_Sugerido'].iloc[0])
                if 'Importe_Sugerido' in filtered_articulo.columns:
                    articulo_importe = float(filtered_articulo['Importe_Sugerido'].iloc[0])
            else:
                st.warning(f"Artículo '{st.session_state.item_selectbox_key}' no encontrado en la base de datos de artículos. Los costes se establecerán en 0.")


        if cliente_id is None:
            st.error("Por favor, selecciona un cliente válido.")
        elif articulo_id is None:
            st.error("Por favor, selecciona un artículo válido.")
        else:
            new_order_data = {
                'Entrega_Cliente': st.session_state.entrega_cliente_input_key,
                'Cliente_id': cliente_id,
                'Articulo_id': articulo_id,
                'Descripcion': st.session_state.descripcion_input_key,
                'Cantidad': st.session_state.cantidad_input_key,
                'Proveedor': st.session_state.proveedor_selectbox_key if st.session_state.proveedor_selectbox_key else None,
                'Pagado': st.session_state.pagado_selectbox_key,
                'Limite': st.session_state.limite_input_key,
                'Coste_Material': articulo_coste_material,
                'Coste_Proveedor': articulo_coste_proveedor,
                'Importe': articulo_importe,
                'Entrega_Proveedor': None, # Estos pueden ser None por defecto al crear
                'Recogida_Proveedor': None,
                'Recogida_Cliente': None,
            }
            
            response = f.insert_record('Pedidos', new_order_data)
            if response:
                st.rerun()
            
# Formulario de búsqueda
with col2:
    st.subheader('Buscar Pedidos')
    formSearch = forms.OrderForm('search','Formulario para Buscar','Buscar registro')

    if formSearch.Button:
        df_display = f.searchFunction(db_joined.copy(), formSearch)
        st.dataframe(df_display, use_container_width=True, hide_index=True) # Añadido hide_index=True

    if formSearch.ButtonReset:
        # Resetear campos de búsqueda
        for key in ['order_search_delivery_date', 'order_search_customer', 'order_search_item', 
                    'order_search_desc', 'order_search_supplier', 'order_search_paid', 'order_search_limit']:
            if key in st.session_state:
                st.session_state[key] = None if 'date' in key or 'limite' in key else '' 
        st.rerun()

# Sección de visualización y edición de datos de pedidos
st.subheader('Datos de Pedidos')

if not db_joined.empty:
    # Definir columnas para la edición
    column_config = {
        "ID": st.column_config.NumberColumn("ID del Pedido", disabled=True),
        "Cliente": st.column_config.TextColumn("Cliente", disabled=True),
        "Articulo": st.column_config.TextColumn("Artículo", disabled=True),
        "Entrega_Cliente": st.column_config.DateColumn("Entrega Cliente", format="DD/MM/YYYY"),
        "Limite": st.column_config.DateColumn("Límite", format="DD/MM/YYYY"),
        "Entrega_Proveedor": st.column_config.DateColumn("Entrega Proveedor", format="DD/MM/YYYY"),
        "Recogida_Proveedor": st.column_config.DateColumn("Recogida Proveedor", format="DD/MM/YYYY"),
        "Recogida_Cliente": st.column_config.DateColumn("Recogida Cliente", format="DD/MM/YYYY"),
        "Pagado": st.column_config.SelectboxColumn(
            "Pagado",
            options=["No Pagado", "Efectivo", "Tarjeta", "Bizum"],
            required=True,
        ),
        "Proveedor": st.column_config.SelectboxColumn(
            "Proveedor",
            options=["", "Alicia", "Dani", "Manuela", "Mari", "Marlen", "Marta"],
            required=False,
        ),
        "Coste_Material": st.column_config.NumberColumn("Coste Material", format="%.2f", step=0.01),
        "Coste_Proveedor": st.column_config.NumberColumn("Coste Proveedor", format="%.2f", step=0.01),
        "Importe": st.column_config.NumberColumn("Importe", format="%.2f", step=0.01),
    }

    edited_db_joined = st.data_editor(db_joined, key='orders_data_editor', column_config=column_config, hide_index=True)

    if st.session_state['orders_data_editor']['edited_rows']:
        st.info("Detectados cambios en el editor de datos. Presiona 'Guardar Cambios' para actualizar.")
        if st.button('Guardar Cambios en Pedidos', key='save_edited_orders'):
            try:
                changes = st.session_state['orders_data_editor']['edited_rows']
                original_df_for_compare = db_joined.copy()

                any_update_successful = False # Se usa para el mensaje final y el rerun
                total_updated_rows = 0

                for index_in_editor, edited_data in changes.items():
                    # Obtener el ID del pedido de la fila original (importante para evitar la confusión de IDs)
                    pedido_id_to_update = original_df_for_compare.loc[index_in_editor, 'ID']

                    update_payload = {}
                    for col, val in edited_data.items():
                        # Excluir las columnas que NO pertenecen a la tabla Pedidos en Supabase
                        # Asegúrate de que 'Cliente' y 'Articulo' se excluyen aquí
                        if col not in ['Cliente', 'Articulo']:
                            if col in ["Entrega_Cliente", "Limite", "Entrega_Proveedor", "Recogida_Proveedor", "Recogida_Cliente"]:
                                if isinstance(val, datetime.date):
                                    update_payload[col] = val.isoformat()
                                elif pd.isna(val) and isinstance(val, pd.Timestamp):
                                    update_payload[col] = None
                                elif pd.isna(val):
                                    update_payload[col] = None
                                else:
                                    update_payload[col] = val
                            elif col in ['Cantidad']:
                                update_payload[col] = int(val) if pd.notna(val) else None
                            elif col in ['Coste_material', 'Coste_proveedor', 'Importe']:
                                update_payload[col] = float(val) if pd.notna(val) else None
                            else:
                                update_payload[col] = val

                    if update_payload: # Solo intentar actualizar si hay datos válidos en el payload
                        result = f.update_record('Pedidos', pedido_id_to_update, update_payload)
                        # La función f.update_record ahora devuelve True/False/None
                        if result is True: # Si update_record devuelve True, fue exitoso
                            any_update_successful = True
                            total_updated_rows += 1
                        else:
                            st.warning(f"Error o no se pudo actualizar el registro ID: {pedido_id_to_update}. Consulta el log para más detalles.")

                # Aquí está la clave: Asegurarse de que el rerun se ejecute si hay ALGUN cambio exitoso
                if any_update_successful:
                    st.success(f"{total_updated_rows} registros de pedidos actualizados con éxito en la base de datos.")
                    time.sleep(1) # Pequeña pausa para ver el mensaje de éxito
                    st.rerun() # <-- ¡Esto fuerza la recarga de la página y la tabla!
                elif not any_update_successful and total_updated_rows == 0: # Si no hubo cambios o ninguno fue exitoso
                    st.info("No se realizaron cambios válidos o no hubo actualizaciones exitosas en los pedidos.")

            except Exception as e:
                st.error(f"Error inesperado durante el proceso de guardar cambios en Pedidos: {e}")



else:
    st.info("No hay pedidos para mostrar. ¡Agrega uno nuevo usando el formulario de arriba!")

f.deleteForm(min_id, max_id, 'Pedidos')