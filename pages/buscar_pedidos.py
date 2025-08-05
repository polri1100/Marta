import streamlit as st
import functions as f
import forms
import pandas as pd
import time
import datetime





st.markdown("# Buscar Pedidos 🔍")

# Load databases (these will not have normalized columns for display)
db_pedidos = f.obtainTable('Pedidos')
db_articulos = f.obtainTable('Articulos')
db_clientes = f.obtainTable('Clientes')

# Join Databases (db_joined will not have normalized columns)
db_joined = f.ordersJoin(db_pedidos, db_clientes, db_articulos)

list_items = db_articulos['Articulo'].unique().tolist() if not db_articulos.empty and 'Articulo' in db_articulos.columns else []
list_items.sort()
placeholder_items = ['-Selecciona Un Artículo-']+list_items
list_customers = db_clientes['Nombre'].unique().tolist() if not db_clientes.empty and 'Nombre' in db_clientes.columns else []
list_customers.sort()
placeholder_customers = ['-Selecciona Un Cliente-']+ list_customers

if 'Cliente_id' in db_joined.columns:
    db_joined = db_joined.drop(columns=['Cliente_id'])
if 'Articulo_id' in db_joined.columns:
    db_joined = db_joined.drop(columns=['Articulo_id'])

# Table calculations
max_id, min_id = f.returnMaxMinID(db_pedidos)

# Initialize displayed_orders_df only if it doesn't exist.
# This ensures that after a rerun (e.g., from reset or update),
# the search results (if any) are preserved, not overwritten by the full table.
if 'df_display_orders' not in st.session_state:
    st.session_state.df_display_orders = db_joined.copy()


# --- Search Form ---
st.subheader('Formulario de Búsqueda')
formSearch = forms.OrderForm('search', '', 'Buscar registro',placeholder_items,placeholder_customers)

if formSearch.Button:
    search_params = {
        'Entrega_Cliente': st.session_state.search_entrega_cliente_value,
        'Cliente': st.session_state.search_customer_value,
        'Articulo': st.session_state.search_item_value,
        'Proveedor': st.session_state.search_proveedor_value,
        'Pagado': st.session_state.search_pagado_value,
        'Limite': st.session_state.search_limite_value,
        'Entrega_Proveedor': st.session_state.search_entrega_proveedor_value,
        'Recogida_Proveedor': st.session_state.search_recogida_proveedor_value,
        'Recogida_Cliente': st.session_state.search_recogida_cliente_value,
    }
    if search_params['Cliente'] == '-Selecciona Un Cliente-':
        del search_params["Cliente"]
    if search_params['Articulo'] == '-Selecciona Un Artículo-':
        del search_params["Articulo"]

    clean_search_params = {k: v for k, v in search_params.items() if v is not None and (isinstance(v, str) and v.strip() != '' or not isinstance(v, str))}

    if clean_search_params:
        filtered_df = f.searchFunction(db_joined.copy(), clean_search_params)
        st.session_state.df_display_orders = filtered_df

        for k in ['search_entrega_cliente_value', 'search_proveedor_value','search_pagado_value','search_limite_value','search_entrega_proveedor_value','search_recogida_proveedor_value','search_recogida_cliente_value']:
            if k in st.session_state:
                del st.session_state[k]


        if filtered_df.empty:
            st.warning("No se encontraron pedidos con esos criterios de búsqueda.",icon="⚠️")
    else:

        # If no search criteria, show all orders
        st.session_state.df_display_orders = db_joined.copy()
        st.info("No se ingresaron criterios de búsqueda. Mostrando todos los pedidos.")

        # After a search, ensure the form's inputs reflect the search values
        # These are already handled by the value=st.session_state.search_... in forms.py
        # So no explicit update needed here, just ensure the form rebuilds with these values.

if formSearch.ButtonReset:
    # Reset the displayed DataFrame to the full table
    st.session_state.df_display_orders = db_joined.copy()
    #st.rerun()

st.markdown("---")
## Visualización y Edición de Pedidos
if not st.session_state.df_display_orders.empty:

    if 'pedidos_changes_detected' not in st.session_state:
        st.session_state.pedidos_changes_detected = False

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
            options=["", "Alicia", "Dani", "Manuela", "Mari", "Marlen","M.Antonia", "Marta"],
            required=False,
            ),
        "Coste_Material": st.column_config.NumberColumn("Coste Material", format="%.2f", step=0.01),
        "Coste_Proveedor": st.column_config.NumberColumn("Coste Proveedor", format="%.2f", step=0.01),
        "Importe": st.column_config.NumberColumn("Importe", format="%.2f", step=0.01),
        "Descripcion": st.column_config.TextColumn("Descripcion"),
        "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1.0, step=1.0),
        }

    edited_df = st.data_editor(
        st.session_state.df_display_orders,
        key='search_orders_data_editor',
        column_config=column_config,
        hide_index=True,
        )

    if st.session_state['search_orders_data_editor']['edited_rows']:
        st.session_state.pedidos_changes_detected = True

    if st.session_state.pedidos_changes_detected:
        st.info("Detectados cambios en el editor de datos. Presiona 'Guardar Cambios' para actualizar.")
        if st.button('Guardar Cambios en Pedidos', key='save_edited_search_orders'):
            try:
                changes = st.session_state['search_orders_data_editor']['edited_rows']
                original_df_for_compare = st.session_state.df_display_orders.copy()
                any_update_successful = False
                total_updated_rows = 0
                for index_in_editor, edited_data in changes.items():
                    pedido_id_to_update = original_df_for_compare.loc[index_in_editor, 'ID']
                    update_payload = {}
                    for col, val in edited_data.items():
                        if col not in ['Cliente', 'Articulo']:
                            if col in ["Entrega_Cliente", "Limite", "Entrega_Proveedor", "Recogida_Proveedor", "Recogida_Cliente"]:
                                if isinstance(val, datetime.date):
                                    update_payload[col] = val.isoformat()
                                elif pd.isna(val) or val == "":
                                    update_payload[col] = None
                                else:
                                    try:
                                        update_payload[col] = pd.to_datetime(val).date().isoformat()
                                    except (ValueError, TypeError):
                                        st.warning(f"Valor no válido para la fecha en la columna '{col}': '{val}'. Se ignorará este campo para la actualización del ID {pedido_id_to_update}.",icon="⚠️")
                                        continue # Skip this field for update_payload
                            elif col in ['Cantidad']:
                                update_payload[col] = int(val) if pd.notna(val) else None
                            elif col in ['Coste_Material', 'Coste_Proveedor', 'Importe']:
                                update_payload[col] = float(val) if pd.notna(val) else None
                            elif pd.isna(val) or val == "": # Catch other empty values and convert to None
                                update_payload[col] = None
                            else:
                                update_payload[col] = val

                    if update_payload:
                        result = f.update_record('Pedidos', pedido_id_to_update, update_payload)
                        if result is True:
                            any_update_successful = True
                            total_updated_rows += 1
                        else:
                            st.warning(f"Error o no se pudo actualizar el registro ID: {pedido_id_to_update}.",icon="⚠️")
                if any_update_successful:
                    st.success(f"{total_updated_rows} pedidos actualizados con éxito!", icon="✅")
                    f.clear_obtain_table_cache()
                    st.session_state.pedidos_changes_detected = False
                    st.session_state['search_orders_data_editor']['edited_rows'] = {}
                    time.sleep(1)
                    st.rerun()
                elif not any_update_successful and total_updated_rows == 0:
                    st.warning("No se realizaron cambios válidos o no hubo actualizaciones exitosas en los pedidos.",icon="⚠️")

            except Exception as e:
                st.error(f"Error inesperado durante el proceso de guardar cambios en Pedidos: {e}")
else:
    st.info("No hay pedidos para mostrar. Usa el formulario de búsqueda para encontrar registros.")

st.markdown("---")

## Eliminar Pedidos

f.deleteForm(min_id, max_id, 'Pedidos')

#st.session_state.df_display_orders = db_joined.copy()
