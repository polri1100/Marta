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
max_id, min_id = f.returnMaxMinID(db_clientes) # Asumiendo que esta función ya es correcta

# --- SECCIÓN DE FORMULARIOS EN COLUMNAS ---
# Crear dos columnas para los formularios
col_insert, col_search = st.columns(2)

# --- FORMULARIO DE INSERCIÓN (En la primera columna) ---
with col_insert:
    st.subheader('Nuevo Cliente')
    formSubmit = forms.CustomerForm('submit', 'Formulario para insertar', 'Insertar registro')

    if formSubmit.Button:
        payload = {
            'Nombre': formSubmit.name,
            'Descripcion': formSubmit.desc, # Asegúrate que 'Descripción' es el nombre correcto de la columna en Supabase
            'Telefono': formSubmit.phone,

        }
        f.insert_record('Clientes', payload)
        st.success("Cliente insertado con éxito.")
        time.sleep(1) # Pequeña pausa para que el usuario vea el mensaje
        st.rerun()

# --- FORMULARIO DE BÚSQUEDA (En la segunda columna) ---
with col_search:
    st.subheader('Buscar Clientes')
    formSearch = forms.CustomerForm('search', 'Formulario para Buscar', 'Buscar registro')

    # Inicializar df_display con la tabla completa por defecto
    df_display = db_clientes.copy()

    # Lógica para manejar el botón de búsqueda
    if formSearch.Button:
        # Construir el diccionario de búsqueda
        search_params = {
            'Nombre': st.session_state.get('customer_search_name_value', ''),
            'Descripcion': st.session_state.get('customer_search_desc_value', ''), # Asegúrate que esta clave es correcta
            'Teléfono': st.session_state.get('customer_search_phone_value', ''),
        }
        
        # Pasa el diccionario de búsqueda a searchFunction
        # Asegúrate de que allowed_columns coincida con los campos que realmente buscas
        df_display = f.searchFunction(db_clientes.copy(), search_params, allowed_columns=['Nombre', 'Descripcion', 'Telefono'])

        if df_display.empty:
            st.info("No se encontraron clientes con esos criterios de búsqueda.")

    # Lógica para manejar el botón de reset de búsqueda
    if formSearch.ButtonReset:
        # Limpiar los valores de session_state para los campos de búsqueda
        st.session_state[f'customer_search_name_value'] = ''
        st.session_state[f'customer_search_desc_value'] = '' # Limpia también la descripción si se usa
        st.session_state[f'customer_search_phone_value'] = ''
        st.rerun() # Recargar la página para limpiar los campos y mostrar la tabla completa

# --- FIN DE LA SECCIÓN DE FORMULARIOS EN COLUMNAS ---

st.markdown("---") # Separador visual entre formularios y tabla

# --- VISUALIZACIÓN DE DATOS (CON EDICIÓN) ---
st.subheader('Datos de Clientes')

# Mostrar el DataFrame, que será el resultado de la búsqueda o el completo por defecto
if not df_display.empty:
    column_config = {
        "ID": st.column_config.NumberColumn("ID del Cliente", disabled=True),
        "Nombre": st.column_config.TextColumn("Nombre"),
        "Descripcion": st.column_config.TextColumn("Descripcion"), # Asegúrate de que esta columna exista
        "Telefono": st.column_config.TextColumn("Telefono"),

    }
    
    # Usar st.data_editor para permitir la edición de clientes
    edited_db_clientes = st.data_editor(df_display, key='clientes_data_editor', column_config=column_config, hide_index=True)

    # Lógica para guardar cambios editados
    if st.session_state['clientes_data_editor']['edited_rows']:
        st.info("Detectados cambios en el editor de datos. Presiona 'Guardar Cambios' para actualizar.")
        if st.button('Guardar Cambios en Clientes', key='save_edited_clientes'):
            try:
                changes = st.session_state['clientes_data_editor']['edited_rows']
                original_df_for_compare = df_display.copy() # Usar df_display aquí, ya que es lo que se editó

                any_update_successful = False
                total_updated_rows = 0

                for index_in_editor, edited_data in changes.items():
                    cliente_id_to_update = original_df_for_compare.loc[index_in_editor, 'ID']
                    update_payload = {}
                    for col, val in edited_data.items():
                        if pd.isna(val):
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
st.markdown("---") # Separador visual
st.subheader('Eliminar Clientes')
f.deleteForm(min_id, max_id, 'Clientes')