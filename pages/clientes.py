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
db_clientes = f.obtainTable('Clientes')

# table calculations
max_id, min_id = f.returnMaxMinID(db_clientes)

# --- SECCIÓN DE FORMULARIOS EN COLUMNAS ---
col_insert, col_search = st.columns(2)

# --- FORMULARIO DE INSERCIÓN (En la primera columna) ---
with col_insert:
    st.subheader('Nuevo Cliente')
    formSubmit = forms.CustomerForm('submit', 'Formulario para insertar', 'Insertar registro')

    if formSubmit.Button:
        payload = {
            'Nombre': formSubmit.name,
            'Descripcion': formSubmit.desc, 
            'Telefono': formSubmit.phone,
        }
        f.insert_record('Clientes', payload)
        st.success("Cliente insertado con éxito.")
        time.sleep(1)
        st.rerun()

# --- FORMULARIO DE BÚSQUEDA (En la segunda columna) ---
with col_search:
    st.subheader('Buscar Clientes')
    formSearch = forms.CustomerForm('search', 'Formulario para Buscar', 'Buscar registro')

    # Initialize df_display with the full table by default
    df_display = db_clientes.copy()

    # Logic to handle search button
    if formSearch.Button:
        # Build the search dictionary using values from session_state
        search_params = {
            'Nombre': st.session_state.get('customer_search_name_value', ''),
            'Descripcion': st.session_state.get('customer_search_desc_value', ''),
            'Telefono': st.session_state.get('customer_search_phone_value', ''), # Corrected column name
        }
        
        # Pass the search dictionary to searchFunction
        # Removed 'allowed_columns' as searchFunction now uses the keys from search_params
        df_display = f.searchFunction(db_clientes.copy(), search_params)

        if df_display.empty:
            st.info("No se encontraron clientes con esos criterios de búsqueda.")

    # Logic to handle reset search button
    if formSearch.ButtonReset:
        # Clear session_state values for search fields
        st.session_state[f'customer_search_name_value'] = ''
        st.session_state[f'customer_search_desc_value'] = ''
        st.session_state[f'customer_search_phone_value'] = ''
        st.rerun() # Recargar la página para limpiar los campos y mostrar la tabla completa

# --- FIN DE LA SECCIÓN DE FORMULARIOS EN COLUMNAS ---

st.markdown("---") # Separador visual entre formularios y tabla

# --- VISUALIZACIÓN DE DATOS (CON EDICIÓN) ---
st.subheader('Datos de Clientes')

if not df_display.empty:
    column_config = {
        "ID": st.column_config.NumberColumn("ID del Cliente", disabled=True),
        "Nombre": st.column_config.TextColumn("Nombre"),
        "Descripcion": st.column_config.TextColumn("Descripcion"),
        "Telefono": st.column_config.TextColumn("Telefono"), # Ensure this matches your DB column name
    }
    
    edited_db_clientes = st.data_editor(df_display, key='clientes_data_editor', column_config=column_config, hide_index=True)

    # Logic to save edited changes
    if st.session_state['clientes_data_editor']['edited_rows']:
        st.info("Detectados cambios en el editor de datos. Presiona 'Guardar Cambios' para actualizar.")
        if st.button('Guardar Cambios en Clientes', key='save_edited_clientes'):
            try:
                changes = st.session_state['clientes_data_editor']['edited_rows']
                original_df_for_compare = df_display.copy()

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
                        result = f.update_record('Clientes', cliente_id_to_update, update_payload)
                        if result is True:
                            any_update_successful = True
                            total_updated_rows += 1
                        else:
                            st.warning(f"Error o no se pudo actualizar el registro ID: {cliente_id_to_update}. Consulta el log para más detalles.")
                
                if any_update_successful:
                    st.success(f"{total_updated_rows} registros de clientes actualizados con éxito en la base de datos.", icon="✅")
                    time.sleep(1)
                    st.rerun()
                elif total_updated_rows == 0 and not any_update_successful:
                    st.info("No se realizaron cambios válidos o no hubo actualizaciones exitosas en los clientes.")

            except Exception as e:
                st.error(f"Error inesperado durante el proceso de guardar cambios en Clientes: {e}")

else:
    st.info("No hay clientes para mostrar.")

# --- FORMULARIO DE ELIMINACIÓN ---
st.markdown("---")
st.subheader('Eliminar Clientes')
f.deleteForm(min_id, max_id, 'Clientes')