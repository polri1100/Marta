import pandas as pd
import streamlit as st
import datetime
from supabase import create_client, Client 
import time

# Cargar credenciales desde secrets.toml
@st.cache_resource # Cachea la conexión a Supabase para no reconectar en cada rerun
def init_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    client: Client = create_client(url, key)
    return client

supabase = init_supabase_client()

# --- Función para obtener tablas (Leer) ---
def obtainTable(table_name):
    try:
        response = supabase.table(table_name).select("*").execute()
        if response.data:
            df = pd.DataFrame(response.data)

            # Convertir columnas de fecha a tipo datetime.date para facilitar la manipulación
            date_columns_map = {
                'Pedidos': ['Entrega_Cliente', 'Limite', 'Entrega_Proveedor', 'Recogida_Proveedor', 'Recogida_Cliente'],
                # Agrega aquí otras tablas y sus columnas de fecha si las tuvieran
            }
            
            if table_name in date_columns_map:
                for col in date_columns_map[table_name]:
                    if col in df.columns:
                        # Convertir a datetime y luego a date object, manejando errores
                        df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
            
            # Asegurarse de que la columna 'ID' sea entera si existe
            if 'ID' in df.columns:
                df['ID'] = pd.to_numeric(df['ID'], errors='coerce').fillna(0).astype(int)

            return df
        else:
            return pd.DataFrame() # Retorna un DataFrame vacío si no hay datos
    except Exception as e:
        st.error(f"Error al obtener datos de la tabla '{table_name}' de Supabase: {e}")
        return pd.DataFrame() # Retorna un DataFrame vacío en caso de error

# --- Función para insertar un registro (Create) ---
def insert_record(table_name, data):
    try:
        # Asegurarse de que los objetos datetime.date se conviertan a strings ISO 8601
        # antes de enviarlos a Supabase
        payload = {}
        for key, value in data.items():
            if isinstance(value, datetime.date):
                payload[key] = value.isoformat()
            else:
                payload[key] = value
        
        response = supabase.table(table_name).insert(payload).execute()

        if response.data:
            st.success(f"Guardado :)", icon="✅")
            return response.data
        elif hasattr(response, 'error') and response.error:
            st.error(f"Error al guardar registro en '{table_name}': {response.error.message} (Código: {response.error.code})")
            return None
        else:
            st.error(f"Error desconocido al guardar registro en '{table_name}'.")
            return None
    except Exception as e:
        st.error(f"Error al insertar registro en '{table_name}': {e}")
        return None

# --- Función para actualizar un registro (Update) ---
def update_record(table_name, record_id, data, id_column_name='ID'):
    try:
        payload = {}
        for key, value in data.items():
            if isinstance(value, datetime.date):
                payload[key] = value.isoformat()
            elif pd.isna(value) and isinstance(value, pd.Timestamp):
                 payload[key] = None
            elif pd.isna(value):
                payload[key] = None
            elif isinstance(value, (int, float)):
                if isinstance(value, float) and value.is_integer():
                    payload[key] = int(value)
                else:
                    payload[key] = value
            else:
                payload[key] = value

        if not payload:
            print(f"Advertencia: No hay datos que actualizar para el registro {record_id} en {table_name}.")
            return None
        
        print(f"\n--- Depuración de Supabase Update ---")
        print(f"Intentando actualizar '{table_name}' con ID '{record_id}'")
        print(f"Payload final a enviar: {payload}")
        print(f"Tipos en payload final: {[type(v) for v in payload.values()]}")

        response = supabase.table(table_name).update(payload).eq(id_column_name, record_id).execute()

        # Las líneas de print de la respuesta cruda de Supabase son CRUCIALES. Mantenlas.
        print(f"Respuesta cruda de Supabase: {response}")
        if hasattr(response, 'data'):
            print(f"response.data: {response.data}")
        if hasattr(response, 'error') and response.error:
            print(f"response.error: {response.error}")

        # La lógica para determinar el éxito.
        # Si no hay un error explícito de Supabase, asumimos éxito.
        if not hasattr(response, 'error') or response.error is None:
            # Incluso si response.data está vacío, si no hay error explícito, es un éxito.
            print(f"Supabase: Actualización sin error explícito. Considerado éxito.")
            return True
        else:
            error_message = response.error.message if hasattr(response.error, 'message') else "Mensaje de error no disponible."
            error_code = response.error.code if hasattr(response.error, 'code') else "Código de error no disponible."
            st.error(f"Error al actualizar registro en '{table_name}' (ID: {record_id}): {error_message} (Código: {error_code})")
            print(f"Error de Supabase: {error_message} (Código: {error_code})")
            return False
    except Exception as e:
        st.error(f"Excepción al actualizar registro en '{table_name}' (ID: {record_id}): {e}")
        print(f"Excepción general en update_record: {e}")
        return False

# --- Función para eliminar un registro (Delete) ---
def delete_record(table_name, record_id, id_column_name='ID'):
    try:
        response = supabase.table(table_name).delete().eq(id_column_name, record_id).execute()
        
        if response.data:
            st.success(f"Borrado :)", icon="✅")
            return response.data
        elif hasattr(response, 'error') and response.error:
            st.error(f"Error al eliminar registro de '{table_name}': {response.error.message} (Código: {response.error.code})")
            return None
        else:
            st.error(f"Error desconocido al eliminar registro de '{table_name}'.")
            return None
    except Exception as e:
        st.error(f"Error al eliminar registro de '{table_name}': {e}")
        return None

# --- Función para retornar Max/Min ID ---
def returnMaxMinID(df):
    if 'ID' in df.columns and not df.empty:
        max_id = df['ID'].max()
        min_id = df['ID'].min()
        return int(max_id), int(min_id)
    else:
        return 0, 0

# --- Función para unir órdenes (Pedidos, Clientes, Articulos) ---
def ordersJoin(db_pedidos, db_clientes, db_articulos):
    if db_pedidos.empty:
        return pd.DataFrame()

    df = db_pedidos.copy()

    # Asegurar que las columnas de ID sean del tipo correcto antes de la unión
    df['Cliente_id'] = pd.to_numeric(df['Cliente_id'], errors='coerce').fillna(0).astype(int)
    df['Articulo_id'] = pd.to_numeric(df['Articulo_id'], errors='coerce').fillna(0).astype(int)

    # --- Paso 1: Unir con Clientes ---
    if not db_clientes.empty and 'ID' in db_clientes.columns:
        db_clientes['ID'] = pd.to_numeric(db_clientes['ID'], errors='coerce').fillna(0).astype(int)
        df = pd.merge(
            df,
            db_clientes[['ID', 'Nombre']].rename(columns={'ID': 'Cliente_Join_ID'}),
            left_on='Cliente_id',
            right_on='Cliente_Join_ID',
            how='left'
        )
        df.rename(columns={'Nombre': 'Cliente'}, inplace=True)
        df.drop(columns=['Cliente_Join_ID'], inplace=True, errors='ignore')

    # --- Paso 2: Unir con Artículos ---
    if not db_articulos.empty and 'ID' in db_articulos.columns:
        db_articulos['ID'] = pd.to_numeric(db_articulos['ID'], errors='coerce').fillna(0).astype(int)

        # Unir y traer las columnas de sugerido
        df = pd.merge(
            df,
            db_articulos[['ID', 'Articulo', 'Coste_Material_Sugerido', 'Coste_Proveedor_Sugerido', 'Importe_Sugerido']].rename(columns={'ID': 'Articulo_Join_ID'}),
            left_on='Articulo_id',
            right_on='Articulo_Join_ID',
            how='left'
        )
        df.rename(columns={'Articulo': 'Articulo_Nombre_Ref'}, inplace=True) # Renombrar temporalmente para evitar conflicto con 'Articulo' si ya existiera en df

        # --- ¡CAMBIO CLAVE AQUÍ! SOBREESCRIBIR LAS COLUMNAS DEL PEDIDO ---
        # Si el Articulo_id no es nulo, sobrescribimos los valores del pedido
        # con los valores sugeridos del artículo.
        # Usa .loc para una asignación segura y evitar SettingWithCopyWarning
        mask_has_article = df['Articulo_id'].notna() & (df['Articulo_id'] != 0)

        # Sobrescribir 'Coste_material' del pedido con 'Coste_Material_Sugerido' del artículo
        df.loc[mask_has_article, 'Coste_material'] = df.loc[mask_has_article, 'Coste_Material_Sugerido']

        # Sobrescribir 'Coste_proveedor' del pedido con 'Coste_Proveedor_Sugerido' del artículo
        df.loc[mask_has_article, 'Coste_proveedor'] = df.loc[mask_has_article, 'Coste_Proveedor_Sugerido']

        # Sobrescribir 'Importe' del pedido con 'Importe_Sugerido' del artículo
        df.loc[mask_has_article, 'Importe'] = df.loc[mask_has_article, 'Importe_Sugerido']

        # Eliminar las columnas *_Sugerido y la de join del DataFrame final
        df.drop(columns=['Coste_Material_Sugerido', 'Coste_Proveedor_Sugerido', 'Importe_Sugerido', 'Articulo_Join_ID'],
                inplace=True, errors='ignore')

        # Si renombraste 'Articulo' a 'Articulo_Nombre_Ref' temporalmente, reestablece el nombre final
        if 'Articulo_Nombre_Ref' in df.columns:
            df.rename(columns={'Articulo_Nombre_Ref': 'Articulo'}, inplace=True)

    # --- Selección y Ordenación Final de Columnas ---
    final_cols = [
        'ID', # ID del pedido
        'Entrega_Cliente',
        'Cliente',
        'Articulo', # Ahora tiene el nombre del artículo
        'Descripcion',
        'Cantidad',
        'Proveedor',
        'Coste_material', # Ya sobrescrito con el sugerido
        'Coste_proveedor', # Ya sobrescrito con el sugerido
        'Importe', # Ya sobrescrito con el sugerido
        'Pagado',
        'Limite',
        'Entrega_Proveedor',
        'Recogida_Proveedor',
        'Recogida_Cliente',
        'Cliente_id', # Mantener las FKs para edición y referencia interna
        'Articulo_id'
    ]

    # Filtrar solo las columnas que realmente existen
    df = df[[col for col in final_cols if col in df.columns]]

    return df

# --- Función para submitDatasource (Insertar/Validar) ---
def submitDatasource(newRow, table_name, uniqueColumn=None, restrictedValue=None):
    # Validaciones previas si uniqueColumn está presente
    if uniqueColumn and newRow.get(uniqueColumn) is not None and newRow.get(uniqueColumn) != '':
        try:
            # Obtener la tabla actual para verificar la unicidad localmente o en Supabase
            existing_data = obtainTable(table_name)
            if not existing_data.empty and uniqueColumn in existing_data.columns:
                # Comprobar si el valor ya existe (insensible a mayúsculas/minúsculas si es texto)
                if newRow[uniqueColumn] in existing_data[uniqueColumn].values: # Comparación exacta
                     st.warning(f'El {uniqueColumn.lower()} "{newRow[uniqueColumn]}" ya existe. No puede haber dos {uniqueColumn.lower()}s iguales.', icon="⚠️")
                     return obtainTable(table_name) # Retorna la tabla actual sin cambios
        except Exception as e:
            st.error(f"Error al verificar unicidad en '{table_name}': {e}")
            return obtainTable(table_name)
    elif uniqueColumn and (newRow.get(uniqueColumn) is None or newRow.get(uniqueColumn) == ''):
        st.warning(f'El campo "{uniqueColumn.lower()}" no puede estar vacío.', icon="⚠️")
        return obtainTable(table_name)

    # Validación específica para el teléfono (si aplica)
    # Suponiendo que restrictedValue es el número de teléfono y uniqueColumn es 'Telefono'
    if uniqueColumn == 'Telefono' and restrictedValue is not None:
        if len(str(restrictedValue)) != 9:
            st.warning('El teléfono debe contener nueve dígitos.', icon="⚠️")
            return obtainTable(table_name)

    # Si todas las validaciones pasan, insertar el registro
    result = insert_record(table_name, newRow)
    if result is not None:
        time.sleep(1) # Pausa breve para que el usuario vea el mensaje de éxito
        st.rerun() # Recarga la aplicación para mostrar la tabla actualizada
    
    return obtainTable(table_name) # Retornar la tabla actualizada (o la que se tenía antes de la inserción si falló)

# --- Función de Búsqueda ---
def searchFunction(df, search_params, allowed_columns=None):
    df_filtered = df.copy()

    # --- CAMBIO CLAVE AQUÍ ---
    # Filtrar search_params para incluir solo las columnas permitidas si allowed_columns no es None
    if allowed_columns:
        search_params_filtered = {k: v for k, v in search_params.items() if k in allowed_columns}
    else:
        search_params_filtered = search_params
    # --- FIN CAMBIO CLAVE ---

    for col, value in search_params_filtered.items():
        if pd.isna(value) or str(value).strip() == '': # Ignorar valores nulos o cadenas vacías/solo espacios
            continue

        # Convertir el valor a string para una búsqueda flexible
        search_value_str = str(value).strip().lower()

        if col in df_filtered.columns:
            # Para columnas de texto, usa contains (ignorando mayúsculas/minúsculas)
            if df_filtered[col].dtype == 'object': # Típicamente el dtype para strings
                df_filtered = df_filtered[
                    df_filtered[col].astype(str).str.contains(search_value_str, case=False, na=False)
                ]
            # Si tienes columnas numéricas o de fecha que también quieres buscar,
            # tendrías que añadir lógica específica aquí (ej. rangos para números/fechas).
            # Para una búsqueda simple por "coincidencia de texto" en números, puedes hacer:
            elif pd.api.types.is_numeric_dtype(df_filtered[col]):
                df_filtered = df_filtered[
                    df_filtered[col].astype(str).str.contains(search_value_str, case=False, na=False)
                ]
            else: # Para otros tipos (fechas, booleanos, etc.), si la conversión a string tiene sentido
                 df_filtered = df_filtered[
                    df_filtered[col].astype(str).str.contains(search_value_str, case=False, na=False)
                ]
        else:
            print(f"Advertencia: Columna '{col}' no encontrada en el DataFrame para la búsqueda.")

    return df_filtered

# --- Función para borrar filas (deleteRow) ---
def deleteRow(table_name, row_id):
    check_unique = False 

    if table_name in ('Articulos', 'Clientes'):
        db_pedidos = obtainTable('Pedidos')
        
        if table_name == 'Articulos':
            if not db_pedidos.empty and 'Articulo_id' in db_pedidos.columns and row_id in db_pedidos['Articulo_id'].values:
                check_unique = True
        elif table_name == 'Clientes':
            if not db_pedidos.empty and 'Cliente_id' in db_pedidos.columns and row_id in db_pedidos['Cliente_id'].values:
                check_unique = True

        if check_unique:
            st.warning(f'No se puede eliminar porque hay un pedido asociado a este {table_name[:-1].lower() if table_name.endswith("s") else table_name}.', icon="⚠️")
            return True # Retorna True si no se pudo eliminar por relación

    # Si no hay relaciones o es la tabla de Pedidos, proceder a eliminar
    if not check_unique:
        delete_record(table_name, row_id, 'ID')
        time.sleep(1) # Pequeña pausa para que el mensaje de éxito/error sea visible
        st.rerun()
    return check_unique

# --- deleteForm se mantiene igual ---
def deleteForm(min_id, max_id, table_name):
    if "deleteButton" not in st.session_state:
        st.session_state.deleteButton = False

    def click_button():
        st.session_state.deleteButton = True

    with st.form(key=f'item-form-delete-{table_name}'):
        st.write("Formulario para Borrar")
        col1, col2 = st.columns([4,1])
        with col1:
            deleteNumber = st.number_input('ID', min_value=min_id, max_value=max_id, value=max_id if max_id > 0 else 0) # Ajuste para min_value y value
        with col2:
            st.form_submit_button('Eliminar registro', on_click=click_button)

    if st.session_state.deleteButton:
        st.warning('¿Estás segura de que quieres borrar? Esta opción no se puede deshacer', icon="⚠️")
        confirmationButton = st.button("¡Sí! Estoy segura", key=f"confirm_delete_{table_name}")

        if confirmationButton:
            st.session_state.deleteButton = False
            deleteRow(table_name, deleteNumber) # Esta función ya maneja los mensajes y reruns


# --- autocomplete_text_input (se mantiene igual) ---
def autocomplete_text_input(label, default_value, suggestions, key):
    if suggestions is None:
        suggestions = []
    
    options = [''] + sorted(list(set(suggestions)))
    
    try:
        if default_value in options:
            index_value = options.index(default_value)
        elif default_value is not None and str(default_value) in options: 
            index_value = options.index(str(default_value))
        elif '' in options:
            index_value = options.index('')
        else:
            index_value = 0 
    except ValueError:
        index_value = 0 

    selected_value = st.selectbox(label, options=options, index=index_value, key=key)
    
    if selected_value == '':
        return None
    
    return selected_value