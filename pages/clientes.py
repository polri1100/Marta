import streamlit as st
import functions as f
import forms
import pandas as pd


#title
st.set_page_config(layout="wide",
                        page_title='Clientes',
                        page_icon='👨‍🦰')
st.markdown("# Clientes 👨‍🦰👩‍🦰")
st.sidebar.markdown("# Clientes 👨‍🦰👩‍🦰")

#table calculations
db_clientes = f.obtainTable('Clientes')
max_id, min_id = f.returnMaxMinID(db_clientes)

#table types 
# phone_nos = db.Telefono.astype(str).replace('^(\d{3})(\d{2})(\d{2})(\d{2})$', r'\1 \2 \3 \4')
# db.Telefono = phone_nos.where(db.Telefono.astype(str).str.contains('^\d{9}$'))

#column formats
col1, col2 = st.columns(2)

# form submit display
with col1:
    formSubmit = forms.CustomerForm('submit', 'Formulario para Insertar','Guardar registro')

#form submit add
if formSubmit.Button:
    
    # new datasource
    new_row_data = {
        'Nombre': formSubmit.name,
        'Descripcion': formSubmit.desc,
        'Telefono': formSubmit.phone
    }
    
    f.submitDatasource(new_row_data, 'Clientes', uniqueColumn='Nombre', restrictedValue=formSubmit.phone)


# form search display
with col2:
    formSearch = forms.CustomerForm('search','Formulario para Buscar','Buscar registro')

    db_display=db_clientes.copy()
# form search filter
if formSearch.Button:
    db_display = f.searchFunction(db_clientes.copy(), formSearch, "Nombre", "Descripcion", "Telefono")

# Lógica para el botón de reseteo de búsqueda
if formSearch.ButtonReset: # Verifica si se presionó el botón de reset
    st.rerun() # Recarga la app para limpiar el formulario de búsqueda y mostrar todos los datos

#table display
st.subheader("Visualización y Edición de Clientes")

if not db_clientes.empty and 'Telefono' in db_clientes.columns:
    db_clientes['Telefono'] = db_clientes['Telefono'].astype(str) # Asegurarse que es string para el data_editor

edited_db_clientes = st.data_editor(
    db_display, # Pasamos el DataFrame que puede estar filtrado
    hide_index=True,
    use_container_width=True,
    key="clientes_data_editor" # Identificador único
)

# Guardar Cambios del Data Editor
if st.button("Guardar Cambios en Clientes"):
    # Re-obtener la tabla original fresca de la DB justo antes de guardar para comparar
    original_db_clientes_for_comparison = f.obtainTable('Clientes')

    # Convertir 'ID' a string en ambos DFs para evitar problemas de tipo en el merge si hubiera
    if 'ID' in original_db_clientes_for_comparison.columns:
        original_db_clientes_for_comparison['ID'] = original_db_clientes_for_comparison['ID'].astype(str)
    if 'ID' in edited_db_clientes.columns:
        edited_db_clientes['ID'] = edited_db_clientes['ID'].astype(str)

    # Identificar filas modificadas usando la funcionalidad de st.data_editor si es posible
    # O bien, una comparación manual más robusta si `st.session_state` no funciona directamente
    
    # La forma más robusta: fusionar y encontrar diferencias
    # Primero, asegurarnos de que ambas tablas tengan el mismo conjunto y orden de columnas
    cols_to_compare = [col for col in edited_db_clientes.columns if col != 'ID']
    
    # Comparar solo las filas con los mismos IDs
    merged_df = pd.merge(edited_db_clientes, original_db_clientes_for_comparison, on='ID', how='left', suffixes=('_edited', '_original'))

    updated_rows_data = []

    for index, row in merged_df.iterrows():
        is_changed = False
        data_for_update = {}
        
        # Validar teléfono antes de cualquier operación
        edited_phone = str(row['Telefono_edited']).strip()
        if not edited_phone.isdigit() or len(edited_phone) != 9:
            st.error(f"Error en el cliente con ID {row['ID']}: El número de teléfono '{edited_phone}' debe tener 9 dígitos numéricos.")
            st.stop() # Detiene la ejecución para que el usuario corrija.

        for col in cols_to_compare:
            edited_val = row[f'{col}_edited']
            original_val = row[f'{col}_original']
            
            # Convertir a string para una comparación uniforme, especialmente si hay NaN o tipos mixtos
            if str(edited_val) != str(original_val):
                is_changed = True
                data_for_update[col] = edited_val
        
        if is_changed:
            updated_rows_data.append({'ID': row['ID'], 'data': data_for_update})

    if updated_rows_data:
        for item in updated_rows_data:
            record_id = item['ID']
            data_to_update = item['data']
            
            if data_to_update: # Asegurarse de que hay algo que actualizar
                f.update_record('Clientes', record_id, data_to_update, id_column_name='ID')
        
        st.success("Cambios guardados exitosamente.")
        st.rerun()
    else:
        st.info("No hay cambios para guardar.")


# delete form
max_id, min_id = f.returnMaxMinID(db_clientes)
f.deleteForm(min_id, max_id, 'Clientes')