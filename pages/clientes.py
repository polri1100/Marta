import streamlit as st
import functions as f
import forms
import pandas as pd
import time

#title
st.set_page_config(layout="wide",
                         page_title='Clientes',
                         page_icon='👨‍🦰')
st.markdown("# Clientes 👨‍🦰👩‍🦰")
st.sidebar.markdown("# Clientes 👨‍🦰👩‍🦰")

# Load database (Clientes)
if 'db_customers' not in st.session_state:
    f.load_and_refresh_data('Clientes')


max_id, min_id = f.returnMaxMinID(st.session_state.db_customers)
# --- SECCIÓN DE FORMULARIOS EN COLUMNAS ---
col_insert, col_search = st.columns(2)

# --- FORMULARIO DE INSERCIÓN (En la primera columna) ---
with col_insert:

    st.subheader('Nuevo Cliente')
    formSubmit = forms.CustomerForm('submit', 'Formulario para insertar', 'Insertar registro')

    if formSubmit.Button:
        nombre_normalizado= f.normalize_string(formSubmit.name)
        nombres_existentes = st.session_state.db_customers['Nombre'].apply(f.normalize_string).tolist()
        if nombre_normalizado in nombres_existentes:
            st.warning("Este cliente ya existe. Intenta con otro nombre o revisa la lista.",icon="⚠️")

        elif not formSubmit.phone.isdigit() or len(formSubmit.phone) != 9:
            st.warning("Teléfono inválido. Ha de tener 9 dígitos y ha de tener solo números")

        else: 
            payload = {
                'Nombre': formSubmit.name,
                'Descripcion': formSubmit.description, 
                'Telefono': formSubmit.phone,
            }
            nomralized_payload = {k:f.normalize_string(v) for k,v in payload.items()}
            f.insert_record('Clientes', nomralized_payload)
            st.success("Cliente insertado con éxito.", icon="✅")
            f.load_and_refresh_data('Clientes')
            st.rerun()

# --- FORMULARIO DE BÚSQUEDA (En la segunda columna) ---
with col_search:
    st.subheader('Buscar Clientes')
    formSearch = forms.CustomerForm('search', 'Formulario para Buscar', 'Buscar registro')

    # Logic to handle search button
    if formSearch.Button:
        # Build the search dictionary using values from session_state
        search_params = {
            'Nombre': formSearch.name,
            'Descripcion': formSearch.description,
            'Telefono': formSearch.phone,
        }
        if search_params['Nombre'] == '-Selecciona Un Cliente-':
            del search_params['Nombre']

        # Pass the search dictionary to searchFunction
        # Removed 'allowed_columns' as searchFunction now uses the keys from search_params
        if search_params:
            filtered_df = f.searchFunction(st.session_state.db_customers.copy(), search_params)
            st.session_state.df_display_clientes = filtered_df

            if filtered_df.empty:
                st.warning("No se encontraron pedidos con esos criterios de búsqueda.",icon="⚠️")

        else:

            # If no search criteria, show all orders
            st.session_state.df_display_orders = st.session_state.db_customers.copy()
            st.info("No se ingresaron criterios de búsqueda. Mostrando todos los pedidos.")


    # Logic to handle reset search button
    if formSearch.ButtonReset:

        st.session_state.df_display_clientes = st.session_state.db_customers.copy()
# --- FIN DE LA SECCIÓN DE FORMULARIOS EN COLUMNAS ---

st.markdown("---") # Separador visual entre formularios y tabla

# --- VISUALIZACIÓN DE DATOS (CON EDICIÓN) ---
st.subheader('Datos de Clientes')

if not st.session_state.df_display_clientes.empty:
    column_config = {
        "ID": st.column_config.NumberColumn("ID del Cliente", disabled=True),
        "Nombre": st.column_config.TextColumn("Nombre"),
        "Descripcion": st.column_config.TextColumn("Descripcion"),
        "Telefono": st.column_config.TextColumn("Telefono"), # Ensure this matches your DB column name
    }
    
    edited_db_clientes = st.data_editor(st.session_state.df_display_clientes, key='clientes_data_editor', column_config=column_config, hide_index=True)

    # Logic to save edited changes
    if st.session_state['clientes_data_editor']['edited_rows']:
        st.info("Detectados cambios en el editor de datos. Presiona 'Guardar Cambios' para actualizar.")
        if st.button('Guardar Cambios en Clientes', key='save_edited_clientes'):
            try:
                changes = st.session_state['clientes_data_editor']['edited_rows']
                original_df_for_compare = st.session_state.df_display_clientes.copy()

                any_update_successful = False
                total_updated_rows = 0

                for index_in_editor, edited_data in changes.items():
                    cliente_id_to_update = original_df_for_compare.loc[index_in_editor, 'ID']
                    update_payload = {}
                    for col, val in edited_data.items():
                        if pd.isna(val) or val == "": # Handle empty string for text fields, and NaN for numbers
                            update_payload[col] = None
                        else:
                            update_payload[col] = val

                    if update_payload:
                        normalized_update_payload = {k:f.normalize_string(v) for k,v in update_payload.items()}
                        result = f.update_record('Clientes', cliente_id_to_update, normalized_update_payload)
                        if result is True:
                            any_update_successful = True
                            total_updated_rows += 1
                        else:
                            st.warning(f"Error o no se pudo actualizar el registro ID: {cliente_id_to_update}.",icon="⚠️")
                
                if any_update_successful:
                    st.success(f"{total_updated_rows} registros de clientes actualizados con éxito en la base de datos.", icon="✅")
                    time.sleep(1)
                    f.load_and_refresh_data('Clientes')
                    st.rerun()
                elif total_updated_rows == 0 and not any_update_successful:
                    st.warning("No se realizaron cambios válidos o no hubo actualizaciones exitosas en los clientes.",icon="⚠️")

            except Exception as e:
                st.error(f"Error inesperado durante el proceso de guardar cambios en Clientes: {e}")

else:
    st.info("No hay clientes para mostrar.")

# --- FORMULARIO DE ELIMINACIÓN ---
st.markdown("---")
st.subheader('Eliminar Clientes')
f.deleteForm(min_id, max_id, 'Clientes')