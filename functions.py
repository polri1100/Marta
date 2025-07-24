import pandas as pd
import streamlit as st
import datetime
from supabase import create_client, Client 
import time
import unidecode

# Cargar credenciales desde secrets.toml
@st.cache_resource # Cachea la conexión a Supabase para no reconectar en cada rerun
def init_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    client: Client = create_client(url, key)
    return client

supabase = init_supabase_client()

def normalize_string(s):
    """Normalizes a string by converting to lowercase, removing accents, and stripping whitespace."""
    if s is None:
        return ""
    return unidecode.unidecode(str(s)).lower().strip()

def obtainTable(tableName):
    """
    Obtains data from a specified Supabase table.
    Returns a pandas DataFrame, or an empty DataFrame if an error occurs.
    """
    try:
        response = supabase.table(tableName).select("*").order("ID", desc=True).limit(1000).execute()
        data = response.data
        if data:
            df = pd.DataFrame(data)
            # Convert date columns to datetime.date objects
            date_columns = {
                'Entrega_Cliente', 'Limite', 'Entrega_Proveedor',
                'Recogida_Proveedor', 'Recogida_Cliente'
            }
            for col in date_columns:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce').dt.date
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al obtener la tabla '{tableName}': {e}")
        return pd.DataFrame()

def obtainTableWithNormalized(tableName):
    """
    Obtains data from a specified Supabase table and adds normalized columns
    for 'Articulo' and 'Nombre'.
    """
    df = obtainTable(tableName)
    if not df.empty:
        if 'Articulo' in df.columns:
            df['Articulo_Normalized'] = df['Articulo'].apply(normalize_string)
        if 'Nombre' in df.columns:
            df['Nombre_Normalized'] = df['Nombre'].apply(normalize_string)
    return df

def returnMaxMinID(df):
    """Returns the maximum and minimum 'ID' from a DataFrame."""
    if not df.empty and 'ID' in df.columns:
        return df['ID'].max(), df['ID'].min()
    return None, None # Return None if DataFrame is empty or 'ID' column is missing

def deleteForm(min_id, max_id, tableName):
    """
    Creates a Streamlit form for deleting a record by ID with confirmation.
    """
    with st.form(key=f'delete-form-{tableName}'):
        st.subheader(f'Eliminar Registro de {tableName}')
        
        # Set default value for ID to the max_id if available, otherwise 1
        default_delete_id = max_id if max_id is not None else 1
        
        id_to_delete = st.number_input(
            f'ID del {tableName} a eliminar', 
            min_value=min_id if min_id is not None else 1, 
            max_value=max_id if max_id is not None else 999999, # A reasonably large upper bound
            value=default_delete_id,
            step=1
        )
        
        # Add a confirmation checkbox
        confirm_delete = st.checkbox(f"Confirmo que deseo eliminar el registro con ID {id_to_delete}")
        
        delete_button = st.form_submit_button('Eliminar Registro')

        if delete_button:
            if confirm_delete:
                if id_to_delete is not None:
                    if delete_record(tableName, int(id_to_delete)):
                        st.success(f"Registro ID {id_to_delete} eliminado con éxito.")
                        load_and_refresh_data(tableName)
                        st.rerun()
                    else:
                        st.error(f"Error al eliminar el registro ID {id_to_delete}.")
                else:
                    st.warning("Por favor, introduce un ID válido para eliminar.")
            else:
                st.warning("Por favor, marca la casilla de confirmación para eliminar el registro.")

def delete_record(tableName, record_id):
    """
    Deletes a record from the specified Supabase table by its ID.
    Returns True on success, False on failure.
    """
    try:
        response = supabase.table(tableName).delete().eq("ID", record_id).execute()
        # Supabase delete operation returns data if successful, otherwise it's an error
        if response.data:
            return True
        else:
            st.error(f"No se encontró el registro con ID {record_id} en la tabla {tableName}.")
            return False
    except Exception as e:
        st.error(f"Error al eliminar registro en {tableName}: Es posible que el cliente tenga registrado un pedido")
        return False

def insert_record(tableName, data):
    """
    Inserts a new record into the specified Supabase table.
    Returns the inserted data on success, None on failure.
    """
    try:
        response = supabase.table(tableName).insert(data).execute()
        if response.data:
            return response.data
        else:
            st.error(f"Error al insertar registro en {tableName}: {response.json()}")
            return None
    except Exception as e:
        st.error(f"Error al insertar registro en {tableName}: {e}")
        return None

def update_record(tableName, record_id, data):
    """
    Updates a record in the specified Supabase table by its ID.
    Returns True on success, False on failure.
    """
    try:
        # Filter out 'None' values from data to avoid updating columns to NULL unintentionally
        # Only update columns that actually have a value (not None) in the payload
        clean_data = {k: v for k, v in data.items() if v is not None}
        
        # Special handling for empty strings for date fields, convert them to None
        for key in ["Entrega_Cliente", "Limite", "Entrega_Proveedor", "Recogida_Proveedor", "Recogida_Cliente"]:
            if key in clean_data and clean_data[key] == "":
                clean_data[key] = None

        response = supabase.table(tableName).update(clean_data).eq("ID", record_id).execute()
        if response.data:
            return True
        else:
            st.error(f"Error al actualizar registro ID {record_id} en {tableName}: {response.json()}")
            return False
    except Exception as e:
        st.error(f"Error al actualizar registro ID {record_id} en {tableName}: {e}")
        return False

def ordersJoin(df_pedidos, df_clientes, df_articulos):
    """
    Performs a join operation between orders, clients, and articles DataFrames.
    Returns the joined DataFrame.
    """
    if df_pedidos.empty:
        return pd.DataFrame()

    # Ensure IDs are integers for merging
    if not df_clientes.empty and 'ID' in df_clientes.columns:
        df_clientes['ID'] = df_clientes['ID'].astype(int)
    if not df_articulos.empty and 'ID' in df_articulos.columns:
        df_articulos['ID'] = df_articulos['ID'].astype(int)
    
    # Merge with Clients
    if not df_clientes.empty:
        df_joined = pd.merge(df_pedidos, df_clientes[['ID', 'Nombre']], 
                             left_on='Cliente_id', right_on='ID', 
                             how='left', suffixes=('', '_Cliente'))
        df_joined = df_joined.rename(columns={'Nombre': 'Cliente'})
        df_joined = df_joined.drop(columns=['ID_Cliente']) # Drop the redundant ID column from merge
    else:
        df_joined = df_pedidos.copy()
        df_joined['Cliente'] = None # Add column even if no data

    # Merge with Articulos
    if not df_articulos.empty:
        df_joined = pd.merge(df_joined, df_articulos[['ID', 'Articulo']], 
                             left_on='Articulo_id', right_on='ID', 
                             how='left', suffixes=('', '_Articulo'))
        df_joined = df_joined.rename(columns={'Articulo_Articulo': 'Articulo'})
        df_joined = df_joined.drop(columns=['ID_Articulo']) # Drop the redundant ID column from merge
    else:
        df_joined['Articulo'] = None # Add column even if no data

    # Reorder columns to place Cliente and Articulo closer to ID
    # Ensure all expected columns are present before reordering
    desired_order = ['ID', 'Cliente', 'Articulo', 'Entrega_Cliente', 'Descripcion', 'Cantidad', 
                     'Proveedor', 'Pagado', 'Limite', 'Coste_Material', 'Coste_Proveedor', 'Importe',
                     'Entrega_Proveedor', 'Recogida_Proveedor', 'Recogida_Cliente']
    
    # Filter desired_order to only include columns actually present in df_joined
    final_columns = [col for col in desired_order if col in df_joined.columns]
    
    return df_joined[final_columns]


def searchFunction(df, search_params):
    """
    Filters a DataFrame based on search parameters.
    It expects search_params to be a dictionary where keys are column names
    and values are the search strings.
    Normalization is applied to string comparisons. Date comparisons are direct.
    
    Args:
        df (pd.DataFrame): The DataFrame to filter.
        search_params (dict): Dictionary of column_name: search_value pairs.
                              Values can be strings (for text search) or datetime.date objects.
    Returns:
        pd.DataFrame: The filtered DataFrame.
    """
    filtered_df = df.copy()

    if filtered_df.empty:
        return pd.DataFrame()

    for column, search_value in search_params.items():
        if search_value is None or (isinstance(search_value, str) and search_value.strip() == ""):
            continue

        if column in filtered_df.columns:
            # Handle date columns
            if isinstance(search_value, datetime.date):
                # Ensure the column is datetime.date type for direct comparison
                if not pd.api.types.is_datetime64_any_dtype(filtered_df[column]):
                    filtered_df[column] = pd.to_datetime(filtered_df[column], errors='coerce').dt.date
                
                # Filter rows where the date matches exactly
                filtered_df = filtered_df[filtered_df[column] == search_value].copy()
            
            # Handle string columns (text search)
            elif pd.api.types.is_string_dtype(filtered_df[column]):
                normalized_search_value = normalize_string(search_value)
                filtered_df = filtered_df[
                    filtered_df[column].astype(str).apply(normalize_string).str.contains(normalized_search_value, na=False)
                ].copy()
            
            # Handle selectbox columns which might have exact string matches but are technically objects
            elif pd.api.types.is_object_dtype(filtered_df[column]) and isinstance(search_value, str):
                # For columns like 'Proveedor' or 'Pagado', an exact match is usually expected if a value is selected
                # But to be safe for partial text search, we can use contains with normalization
                normalized_search_value = normalize_string(search_value)
                filtered_df = filtered_df[
                    filtered_df[column].astype(str).apply(normalize_string).str.contains(normalized_search_value, na=False)
                ].copy()
            
            # Handle numeric or other types for exact match if value is not string/date
            else:
                filtered_df = filtered_df[filtered_df[column] == search_value].copy()
        
        if filtered_df.empty:
            break # No need to continue if the DataFrame is already empty

    return filtered_df

# --- Función para regenerar el DataFrame unido de pedidos ---
def regenerate_joined_orders_df():
    """
    Regenera st.session_state.db_full_orders_joined utilizando los datos más recientes
    de Pedidos, Clientes y Articulos de session_state.
    Luego, actualiza st.session_state.df_display_orders con este DataFrame unido completo.
    """
    # Asegúrate de que estas claves existan antes de usarlas
    # Si alguna no existe (ej. al inicio), usa un DataFrame vacío
    pedidos_df = st.session_state.get('db_orders', pd.DataFrame())
    clientes_df = st.session_state.get('db_customers', pd.DataFrame())
    articulos_df = st.session_state.get('db_articulos', pd.DataFrame())

    # Genera el DataFrame unido
    joined_df = ordersJoin(pedidos_df, clientes_df, articulos_df)
    
    # Almacena el DataFrame unido completo en session_state para referencia
    st.session_state.db_full_orders_joined = joined_df
    
    # Y, crucialmente, actualiza el DataFrame que se muestra en la UI para pedidos
    st.session_state.df_display_orders = joined_df.copy()


def load_and_refresh_data(table_name):
    """
    Carga los datos de una tabla específica desde la base de datos
    y actualiza las variables de session_state correspondientes.
    
    table_name: El nombre de la tabla (ej. 'Clientes', 'Articulos', 'Pedidos').
    """
    # Define las claves de session_state que corresponden a cada tabla
    db_key = None
    # display_key = None # Ya no necesitamos un display_key separado para Pedidos aquí
    
    if table_name == 'Clientes':
        db_key = 'db_customers'
        display_key = 'df_display_clientes' # Todavía útil para clientes/artículos
    elif table_name == 'Articulos':
        db_key = 'db_articulos'
        display_key = 'df_display_articulos' # Todavía útil para clientes/artículos
    elif table_name == 'Pedidos':
        db_key = 'db_orders'
        # Para Pedidos, df_display_orders siempre se deriva del join, no de db_orders directamente
        # Por lo tanto, no asignamos display_key aquí para Pedidos.
    else:
        st.error(f"Configuración de session_state no definida para la tabla: {table_name}")
        return

    # Cargar los datos frescos de la base de datos para la tabla específica
    st.session_state[db_key] = obtainTable(table_name)
    
    # Después de cargar la tabla, regenera el DataFrame unido de pedidos
    # Esto es importante porque cualquier cambio en Pedidos, Clientes o Articulos
    # afecta al DataFrame unido.
    if 'db_orders' in st.session_state and 'db_customers' in st.session_state and 'db_articulos' in st.session_state:
        # Solo regenerar si las tres tablas base necesarias para el join ya están en session_state
        # Esto evita errores al inicio si no todas están cargadas aún.
        regenerate_joined_orders_df()
    
    # Para tablas que no son pedidos y no tienen un 'join' asociado para la visualización,
    # actualiza su propio DataFrame de visualización
    if table_name in ['Clientes', 'Articulos']:
        st.session_state[display_key] = st.session_state[db_key].copy()