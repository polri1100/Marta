import pygsheets
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
def obtainTable(table_name): # table_name ahora es el nombre de la tabla en Supabase (ej. 'Articulos', 'Clientes', 'Pedidos')
    try:
        response = supabase.table(table_name).select("*").execute()
        data = response.data
        df = pd.DataFrame(data)

        # Post-procesamiento para fechas en la tabla 'Pedidos'
        if table_name == 'Pedidos':
            for col in ['Fecha_Entrega', 'Fecha_Recogida']:
                if col in df.columns:
                    df[col] = pd.to_datetime(df[col], errors='coerce', format='%Y-%m-%d', dayfirst=False)
            
            # Convertir 'Pagado' de Supabase (que podría ser bool o cadena si se importó así) a booleano de Python
            if 'Pagado' in df.columns:
                # Supabase debería devolverlo como booleano, pero si hay inconsistencias previas:
                df['Pagado'] = df['Pagado'].astype(bool)

        # Post-procesamiento para Articulos y Clientes si tienen ID_x/Descripcion_x de joins anteriores
        # Esto es para asegurar que los DataFrames individuales de 'Articulos' y 'Clientes'
        # tengan los nombres de columna correctos si esta función se llama para esos.
        # Asumo que en las tablas base de Supabase, las columnas son Articulo, Descripcion, Nombre, etc.
        # y no tienen sufijos como _x.
        # Si db_pedidos después de joins tiene ID_x, eso se mapeará en ordersJoin, no aquí.

        return df

    except Exception as e:
        st.error(f"Error al obtener datos de la tabla '{table_name}' de Supabase: {e}")
        return pd.DataFrame() # Retorna un DataFrame vacío en caso de error
  

# --- Función para insertar un registro (Create) ---
def insert_record(table_name, data):
    try:
        print(data)
        print(table_name)
        response = supabase.table(table_name).insert(data).execute()

        # Verifica si hay datos en la respuesta. Si hay, la inserción fue exitosa.
        if response.data:
            st.success(f"Guardado :)", icon="✅")
            return response.data # Devolver los datos insertados
        else:
            # Si response.data está vacío, algo salió mal
            st.error(f"Error al guardar registro en '{table_name}': No se recibieron datos de confirmación.")
            return None
    except Exception as e:
        st.error(f"Error al insertar registro en '{table_name}': {e}")
        return None

# --- Función para actualizar un registro (Update) ---
def update_record(table_name, record_id, data, id_column_name='ID'):
    try:
        
        # Si 'ID' (o cualquier otro PK) está en `data`, debe eliminarse, ya que solo se usa para la condición `eq`.
        # Esto es crucial para evitar errores de Supabase.
        if id_column_name in data:
            del data[id_column_name]

        # Asegurarse de que 'data' no esté vacío antes de llamar a update
        if not data:
            print(f"Advertencia: No hay datos que actualizar para el registro {record_id} en {table_name}.")
            return None # No hay nada que hacer

        response = supabase.table(table_name).update(data).eq(id_column_name, record_id).execute()
        
        if response.data:
            st.success(f"Actualizado :)", icon="✅")
            return response.data
        else:
            st.error(f"Error al actualizar registro en '{table_name}': No se recibieron datos de confirmación.")
            return None
    except Exception as e:
        st.error(f"Error al actualizar registro en '{table_name}': {e}")
        return None

# --- Función para eliminar un registro (Delete) ---
def delete_record(table_name, record_id, id_column_name='ID'):
    try:
        # La operación de delete devuelve los registros eliminados en response.data
        response = supabase.table(table_name).delete().eq(id_column_name, record_id).execute()
        
        # Verificar si la lista de datos devuelta no está vacía para confirmar la eliminación
        # Aquí es donde estaba el problema potencial con status_code.
        # Solo verificamos si response.data tiene contenido.
        if response.data:
            st.success(f"Borrado :)", icon="✅")
            return response.data
        else:
            # Si response.data está vacío, es posible que el registro no existiera o que RLS lo bloqueó
            st.error(f"Error al eliminar registro de '{table_name}': No se encontró el registro o la operación fue bloqueada.")
            return None
    except Exception as e:
        st.error(f"Error al eliminar registro de '{table_name}': {e}")
        return None


#def uploadTable(db, sheetName): Ya no la usamos 


# --- Función para mostrar tabla (Display) ---
def displayTable(db, sortField='ID'): # 'ID' debería ser la columna 'ID' de Supabase
    # Asegurarse de que la columna de ordenación exista
    if sortField in db.columns:
        db = db.sort_values(by=[sortField], ascending=False)
    else:
        st.warning(f"La columna '{sortField}' no existe para ordenar. Mostrando sin ordenar.")
    st.dataframe(db, hide_index=True, use_container_width=True) # Usar st.dataframe, st.data_editor es para edición directa


# --- Función para retornar Max/Min ID ---
def returnMaxMinID(db):
    if 'ID' in db.columns and not db['ID'].empty:
        max_id = db['ID'].max()
        min_id = db['ID'].min()
        return int(max_id), int(min_id) # Asegurar que sean enteros para st.number_input
    else:
        return 0, 0 # O un valor apropiado si no hay IDs aún

# --- Función para unir órdenes (Pedidos, Clientes, Articulos) ---
def ordersJoin(db_pedidos, db_clientes, db_articulos):
    # Asegúrate de que las columnas de unión existen y son del tipo adecuado.
    # Los IDs en Supabase son normalmente enteros.
    # Renombra tus columnas en Supabase para evitar los sufijos como _x, _y, etc.
    # Pero si los tienes, aquí los mapeamos.

    # 1. Asegurar que los IDs para la unión son del mismo tipo y existen
    #    Asumiendo que 'ID' en Articulos y Clientes es el ID primario.
    #    Y que Pedidos tiene Cliente_id y Articulo_id.
    
    # Conversión de tipos si fuera necesario, aunque Supabase debería manejarlos bien
    db_pedidos['Cliente_id'] = db_pedidos['Cliente_id'].astype(int)
    db_pedidos['Articulo_id'] = db_pedidos['Articulo_id'].astype(int)
    db_clientes['ID'] = db_clientes['ID'].astype(int)
    db_articulos['ID'] = db_articulos['ID'].astype(int)

    # 2. Realizar las uniones
    # Asegúrate de que las columnas 'ID' de clientes/articulos y 'Cliente_id'/'Articulo_id' de pedidos
    # son los nombres de columna EXACTOS en tus tablas de Supabase.
    
    # Manejar posibles valores nulos en columnas de unión
    db_pedidos_filtered = db_pedidos[db_pedidos['Cliente_id'].notna()]
    db_pedidos_filtered = db_pedidos_filtered[db_pedidos_filtered['Articulo_id'].notna()]


    db_joined = db_pedidos_filtered.merge(db_clientes, left_on='Cliente_id', right_on='ID', how='left', suffixes=('_pedido', '_cliente'))
    db_joined = db_joined.merge(db_articulos, left_on='Articulo_id', right_on='ID', how='left', suffixes=('_joined', '_articulo'))

    # Seleccionar y renombrar columnas para la visualización final
    # NOMBRES DE COLUMNAS AQUI DEBEN COINCIDIR CON LOS NOMBRES FINALES DESEADOS EN LA TABLA MOSTRADA
    # Y los nombres con sufijo _pedido, _cliente, _articulo, _joined deben ser los que resultaron del merge
    # Basado en tu código anterior, parece que esperas estas columnas:
    final_columns = {
        'ID_pedido': 'ID', # El ID del pedido
        'Fecha_Entrega': 'Fecha_Entrega',
        'Nombre': 'Nombre', # Del cliente
        'Articulo': 'Articulo', # Del artículo
        'Descripcion_pedido': 'Descripcion', # Descripción del pedido (si hay una)
        'Cantidad': 'Cantidad',
        'Coste': 'Coste',
        'Precio': 'Precio',
        'Pagado': 'Pagado',
        'Fecha_Recogida': 'Fecha_Recogida'
    }
    
    # Si 'Descripcion_x' es realmente 'Descripcion_pedido' del merge
    # Y si tus columnas en Supabase no tienen 'ID_x' o 'ID_y' sino 'ID' para las tablas originales,
    # el sufijo ID_pedido es para el ID del pedido, el original.

    # Verificar si las columnas con sufijos existen antes de seleccionarlas
    # Esto es crucial si los nombres de columnas de Supabase no generan exactamente estos sufijos
    
    # Renombrar columnas para la salida final
    # Asegúrate que los nombres de columna en el diccionario final_columns existan en db_joined
    # antes de intentar seleccionarlos o renombrarlos.
    
    # Primero, ajustamos los nombres para que el merge resulte en los nombres correctos
    # Para la Descripción, tu código anterior tenía 'Descripcion_x'. 
    # Si la descripción de los pedidos es 'Descripcion' y la de los artículos es 'Descripcion',
    # el merge por defecto las nombrará 'Descripcion_x' y 'Descripcion_y'.
    # Si la columna Descripción del pedido en Supabase es simplemente 'Descripcion', se llamará así.
    # Si la de los artículos también es 'Descripcion', el merge la renombrará a 'Descripcion_articulo'.
    # Aquí asumiremos que 'Descripcion_pedido' es la descripción del pedido.

    # Verificar existencia de columnas después del merge
    cols_to_select = []
    # Usar .get() para evitar KeyError si una columna no existe después del merge
    # Esto es una suposición basada en cómo suelen quedar los merges.
    # Revisa los DataFrames intermedios para confirmarlo si tienes problemas.
    if 'ID_pedido' in db_joined.columns: cols_to_select.append('ID_pedido')
    if 'Fecha_Entrega' in db_joined.columns: cols_to_select.append('Fecha_Entrega')
    if 'Nombre' in db_joined.columns: cols_to_select.append('Nombre')
    if 'Articulo' in db_joined.columns: cols_to_select.append('Articulo')
    if 'Descripcion_pedido' in db_joined.columns: cols_to_select.append('Descripcion_pedido')
    if 'Cantidad' in db_joined.columns: cols_to_select.append('Cantidad')
    if 'Coste' in db_joined.columns: cols_to_select.append('Coste')
    if 'Precio' in db_joined.columns: cols_to_select.append('Precio')
    if 'Pagado' in db_joined.columns: cols_to_select.append('Pagado')
    if 'Fecha_Recogida' in db_joined.columns: cols_to_select.append('Fecha_Recogida')

    db_joined = db_joined[cols_to_select]

    # Renombrar a los nombres finales esperados en la UI
    # Usar .get() para el renombrado también para mayor robustez
    rename_mapping = {
        'ID_pedido': 'ID',
        'Fecha_Entrega': 'Fecha_Entrega',
        'Descripcion_pedido': 'Descripcion',
        'Fecha_Recogida': 'Fecha_Recogida'
    }
    db_joined.rename(columns=rename_mapping, inplace=True)
    
    # Conversiones de tipo adicionales para las columnas de fecha si es necesario después del merge
    for col in ['Fecha_Entrega', 'Fecha_Recogida']:
        if col in db_joined.columns:
            db_joined[col] = pd.to_datetime(db_joined[col], errors='coerce').dt.date # Para mostrar solo la fecha

    return db_joined

# --- Función para submitDataSource (Insertar/Validar) ---
def submitDatasource(newRow, table_name, uniqueColumn=None, restrictedValue=''):
    # Esta función necesita ser reescrita para usar insert_record y las validaciones.
    # Ya no concatena DataFrames localmente para luego subirlos.
    # Ahora inserta directamente en Supabase.

    if uniqueColumn is not None:
        if newRow[uniqueColumn] == [''] or newRow[uniqueColumn] == '':
            st.warning(f'El {uniqueColumn.lower()} no puede estar vacio', icon="⚠️")
            return obtainTable(table_name) # Retorna la tabla actual sin cambios

        # Verificar si el valor ya existe en Supabase
        try:
            response = supabase.table(table_name).select(uniqueColumn).eq(uniqueColumn, newRow[uniqueColumn]).execute()
            if response.data:
                st.warning(f'El {uniqueColumn.lower()} ya existe. No puede haber dos {uniqueColumn.lower()}s iguales.', icon="⚠️")
                return obtainTable(table_name)
        except Exception as e:
            st.error(f"Error al verificar unicidad en '{table_name}': {e}")
            return obtainTable(table_name)


    if len(str(restrictedValue)) == 9 or restrictedValue == '': # Asumo que restrictedValue es el teléfono
        pass
    else:
        st.warning('El telefono debe contener nueve digitos', icon="⚠️")
        return obtainTable(table_name)

    # Si todas las validaciones pasan, insertar el registro
    # newRow es un diccionario o similar que se puede pasar directamente a insert_record
    result = insert_record(table_name, newRow)
    if result is not None:
        time.sleep(3) # Pausa de 3 segundos
        st.rerun()

    return obtainTable(table_name) # Retornar la tabla actualizada


# --- Función de Búsqueda (ya estaba adaptada en la revisión anterior) ---
def searchFunction(db, instance, *args):
    formSearchArgsList = []
    for i in instance.__dict__.keys():
        if i not in ('title', 'Button', 'ButtonReset', 'suggestedButton'):
            formSearchArgsList.append(i)

    for count, j in enumerate(formSearchArgsList):
        instAtr = getattr(instance, j)

        if instAtr is None or instAtr == '' or instAtr == ' ':
            pass
        elif type(instAtr) is datetime.date:
            db_column_name = args[count]
            # La conversión a datetime ya debería haberse hecho en obtainTable o al cargar el DF.
            # Aquí solo nos aseguramos de comparar la parte de la fecha.
            if db_column_name in db.columns and pd.api.types.is_datetime64_any_dtype(db[db_column_name]):
                db = db.loc[
                    (db[db_column_name].dt.date == instAtr) &
                    (db[db_column_name].notna())
                ]
            else:
                st.warning(f"La columna '{db_column_name}' no es de tipo fecha/hora en el DataFrame para búsqueda.")
                # Si la columna no es de fecha/hora, no la usamos para filtrar por fecha
                continue


        elif type(instAtr) is bool:
            if args[count] in db.columns: # Asegurarse de que la columna existe
                db = db.loc[db[args[count]] == instAtr]
        else:
            if instAtr not in (' '):
                if args[count] in db.columns: # Asegurarse de que la columna existe
                    # Convertir ambos a minúsculas para la comparación case-insensitive
                    db = db[db[args[count]].astype(str).str.lower().str.contains(str(instAtr).lower(), na=False)]
    return db


# --- Función para borrar filas (deleteRow) ---
def deleteRow(table_name, row_id): # row_id será el valor de la columna 'ID'
    # Esta función debe usar delete_record de Supabase
    
    check_unique = False # Para saber si se encontró un pedido relacionado

    if table_name in ('Articulos', 'Clientes'):
        db_pedidos = obtainTable('Pedidos')
        
        # Obtener el ID de la tabla actual (Articulos o Clientes)
        # Esto asume que 'ID' es la clave primaria en Articulos/Clientes.
        # id_objeto = db.loc[db['ID'] == row_id]['ID'].values[0] # Esto ya no es necesario

        if table_name == 'Articulos':
            # Verificar si hay pedidos que referencien este Articulo_id
            if db_pedidos['Articulo_id'].isin([row_id]).any():
                check_unique = True
        else: # Clientes
            # Verificar si hay pedidos que referencien este Cliente_id
            if db_pedidos['Cliente_id'].isin([row_id]).any():
                check_unique = True

        if check_unique:
            st.warning(f'No se puede eliminar porque hay un pedido con este {table_name[:-1].lower()}', icon="⚠️") # Ej. articulo
            return True # Retorna True si no se pudo eliminar por relación

    # Si no hay relaciones o es la tabla de Pedidos, proceder a eliminar
    if not check_unique:
        delete_record(table_name, row_id, 'ID') # Asumiendo 'ID' es la columna principal
        # Ya no necesitamos uploadTable aquí porque delete_record maneja la eliminación en Supabase.
        time.sleep(3)
        st.rerun() # Recarga la aplicación para mostrar los cambios

    return check_unique # Retorna si se pudo eliminar o no (False = eliminado, True = no se pudo por relación)

# --- deleteForm se mantiene igual, ya que llama a deleteRow ---
def deleteForm(min_id, max_id, table_name): # Renombrado fileName a table_name

    if "deleteButton" not in st.session_state:
        st.session_state.deleteButton = False

    def click_button():
        st.session_state.deleteButton = True

    with st.form(key=f'item-form-delete-{table_name}'): # Añadir table_name a la key para unicidad
        st.write("Formulario para Borrar")
        col1, col2 = st.columns([4,1])
        with col1:
            deleteNumber = st.number_input('ID', min_value=min_id, max_value=max_id, value=max_id)

        with col2:
            st.form_submit_button('Eliminar registro', on_click=click_button)

    if st.session_state.deleteButton:
        st.session_state.deleteButton = True # Mantener como True hasta confirmación
        st.warning('¿Estás segura que quieres borrar? Esta opción no se puede deshacer')
        confirmationButton = st.button("¡Sí! Estoy segura", key=f"confirm_delete_{table_name}") # Clave única

        if confirmationButton: # Solo si se confirma
            st.session_state.deleteButton = False # Resetear el estado del botón
            checkunique = deleteRow(table_name, deleteNumber)
            # El mensaje de éxito/advertencia ahora viene de deleteRow/delete_record
            # if not checkunique:
            #     st.success('Borrado :)', icon="✅") # Esto se duplicaría con el de delete_record
            st.rerun() # Esto asegura que la tabla se refresque después de la operación


# def save_data(db, sheetName): YA NO LA USAMOS




# --- autocomplete_text_input (se mantiene igual, no depende de la fuente de datos) ---
# La función ya estaba bien definida y es genérica.
def autocomplete_text_input(label, default_value, suggestions, key):
    # Asegurarse de que suggestions siempre sea una lista
    if suggestions is None:
        suggestions = []
    
    # Asegurarse de que la opción por defecto esté en la lista si no es vacía
    # Esto es para que st.selectbox no falle si default_value no está en suggestions
    options = [''] + sorted(list(set(suggestions))) # Añadir una opción vacía y ordenar/eliminar duplicados
    
    # Determinar el índice inicial
    if default_value in options:
        index_value = options.index(default_value)
    elif '' in options: # Selecciona la opción vacía si no hay default_value y está disponible
        index_value = options.index('')
    else: # Último recurso, selecciona el primer elemento
        index_value = 0

    selected_value = st.selectbox(label, options=options, index=index_value, key=key)
    
    # Si la opción vacía ('') es seleccionada, devolver None
    if selected_value == '':
        return None
    
    return selected_value