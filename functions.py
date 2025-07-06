import pygsheets
import pandas as pd
import streamlit as st
import datetime
import json

def obtainSheet(sheetName):

    client = pygsheets.authorize(service_account_file="credentials.json")


    excel = client.open_by_url('https://docs.google.com/spreadsheets/d/1pz_MPwerlbM5--sAdBykbcImsRL-zNGezqLI69oX-ac/edit?usp=sharing')
    sheet = excel.worksheet_by_title(sheetName)

    return sheet

def obtainTable(sheetName):
    
    sheet = obtainSheet(sheetName)
    db = sheet.get_as_df()
    return db

def uploadTable(db, sheetName):

    sheet = obtainSheet(sheetName)
    sheet.resize(db.shape[0],db.shape[1])
    sheet.set_dataframe(db, start= (1,1))

def displayTable(db, sortField='ID'):

    db = db.sort_values(by=[sortField], ascending=False)
    st.data_editor(db, hide_index=True, use_container_width=True)

def returnMaxMinID(db):
    max_id = db['ID'].max()
    min_id = db['ID'].min()

    return max_id, min_id

def ordersJoin(db_pedidos, db_clientes, db_articulos):
    
    db_pedidos["Pagado"] = db_pedidos["Pagado"].map({"TRUE":True, "FALSE":False}).astype("bool") #necesario para el valor sea booleano

    db_joined = db_pedidos.merge(db_clientes, left_on='Cliente_id', right_on='ID', how='left')
    db_joined = db_joined.merge(db_articulos, left_on='Articulo_id', right_on='ID', how='left')
    db_joined = db_joined[['ID_x', 'Fecha Entrega', 
                        'Nombre',
                        'Articulo', 'Descripcion_x',
                        'Cantidad', 'Coste', 'Precio',
                        'Pagado', 'Fecha Recogida']]
    db_joined['Fecha Entrega'] = pd.to_datetime(db_joined['Fecha Entrega'], format="%Y-%m-%d")
    db_joined['Fecha Recogida'] = pd.to_datetime(db_joined['Fecha Recogida'], format="%Y-%m-%d")
    db_joined.rename(columns={'ID_x': 'ID'}, inplace=True)
    db_joined.rename(columns={'Descripcion_x': 'Descripcion'}, inplace=True)

    return db_joined

def submitDatasource(newRow, fileName, uniqueColumn=None, restrictedValue=''):

    df_new = pd.DataFrame(newRow)
    df_existing = obtainTable(fileName)

    if fileName == 'pedidos':
        df_new['Fecha Entrega'] = pd.to_datetime(df_new['Fecha Entrega'], format="%Y-%m-%d")
        df_new['Fecha Recogida'] = pd.to_datetime(df_new['Fecha Recogida'], format="%Y-%m-%d")
        
        df_existing['Fecha Entrega'] = pd.to_datetime(df_existing['Fecha Entrega'], format="%Y-%m-%d")
        df_existing['Fecha Recogida'] = pd.to_datetime(df_existing['Fecha Recogida'], format="%Y-%m-%d")

    if uniqueColumn is not None: 
        if newRow[uniqueColumn] == ['']:
            st.warning('El nombre no puede estar vacio', icon="⚠️")
            return df_existing
    
        if newRow[uniqueColumn] in df_existing[uniqueColumn].values:
            st.warning('El nombre ya existe. No puede haber dos {}s iguales'.format(uniqueColumn.lower()), icon="⚠️")
            return df_existing

    if len(restrictedValue) == 9 or restrictedValue == '':
        pass
    else:
        st.warning('El telefono debe contener nueve digitos', icon="⚠️")
        return df_existing

    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
    uploadTable(df_combined, fileName)
    st.success('Añadido :)', icon="✅")
    df_combined = obtainTable(fileName)

    return df_combined

def searchFunction(db, instance, *args):
    formSearchArgsList = []
    for i in instance.__dict__.keys():
        if i not in ('title', 'Button', 'ButtonReset'):
            formSearchArgsList.append(i)

    for count, j in enumerate(formSearchArgsList):
        instAtr =  getattr(instance, j)
        if instAtr is None:
            pass
        elif type(instAtr) is datetime.date:
            dt_obj = datetime.datetime.strptime(str(instAtr),'%Y-%m-%d')
            dt_obj = dt_obj.strftime('%d/%m/%Y')
            db = db.loc[db[args[count]]==dt_obj]
        elif type(instAtr) is bool:
            db = db.loc[db[args[count]]==instAtr]
        else:
            if instAtr not in (' '):
                db = db[db[args[count]].astype(str).str.lower().str.contains(str(instAtr).lower(), na=False)]

    return db

def deleteRow(fileName, row):

    if fileName in ('articulos', 'clientes'):
        db_pedidos = obtainTable('pedidos')
        db = obtainTable(fileName)

        id_objeto = db.loc[db['ID'] == row]['ID'].values[0]

        if fileName == 'articulos':
            checkunique = id_objeto in db_pedidos['Articulo_id'].values
        else: 
            checkunique = id_objeto in db_pedidos['Cliente_id'].values

        if checkunique:
            return st.warning('No se puede eliminar porque hay un pedido con este {}'.format(fileName), icon="⚠️")

    db = obtainTable(fileName)
    db = db[db.ID != row]
    uploadTable(db, fileName)
    st.rerun()

    return checkunique

def deleteForm(min_id, max_id, fileName):

    if "deleteButton" not in st.session_state:
        st.session_state.deleteButton = False

    def click_button():
        st.session_state.deleteButton = True

    with st.form(key='item-form-delete'):
        st.write("Formulario para Borrar")
        #column formats
        col1, col2 = st.columns([4,1])
        with col1:
            deleteNumber = st.number_input('ID', min_value=min_id, max_value=max_id, value=max_id)

        with col2:
            st.form_submit_button('Eliminar registro', on_click=click_button)

    if st.session_state.deleteButton:
        st.session_state.deleteButton = True
        st.warning('Estas segura que quieres borrar? Esta opcion no se puede deshacer')
        confirmationButton = st.button("Si! Estoy segura")

        # If confirmation button is not clicked, stop execution
        if not confirmationButton:
            return
        
        if st.session_state.deleteButton and confirmationButton:
            st.session_state.deleteButton = False
            checkunique = deleteRow(fileName, deleteNumber)
            if not checkunique:
                st.success('Borrado :)', icon="✅")

def save_data(db, sheetName):

    try:
        sheet = obtainSheet(sheetName)
        sheet.resize(db.shape[0], db.shape[1]) #el tamaño ha de ser el mismo
        sheet.set_dataframe(db, start=(1, 1))  # Carga el DataFrame en la hoja, desde la celda A1 (1,1)
        st.success(f"¡Cambios guardados en la hoja '{sheetName}' con éxito!")
    except Exception as e:
        st.error(f"Error al guardar los cambios en la hoja '{sheetName}': {e}")


def autocomplete_text_input(label, current_value, options_list, form_key_suffix):
    """
    Muestra un text_input y, si hay valor, un selectbox con sugerencias.
    Retorna el valor seleccionado o el valor del text_input si no hay selección.
    """
    # La key del text_input debe ser única
    text_input_key = f"{label}_text_{form_key_suffix}"
    text_input_value = st.text_input(label, value=current_value, key=text_input_key)

    selected_suggestion = text_input_value # Valor por defecto si no hay sugerencia seleccionada

    if text_input_value:
        # Filtrar opciones basadas en la entrada (case-insensitive)
        filtered_options = [
            opt for opt in options_list
            if text_input_value.lower() in str(opt).lower()
        ]

        if filtered_options:
            # Añadir una opción vacía para permitir deseleccionar
            display_options = [""] + sorted(filtered_options)

            default_index = 0
            if text_input_value.lower() in [s.lower() for s in filtered_options]:
                try:
                    # Busca la posición exacta del valor actual en la lista de opciones
                    # para preseleccionar si ya ha escrito algo que es una opción completa
                    for i, opt in enumerate(display_options):
                        if str(opt).lower() == text_input_value.lower():
                            default_index = i
                            break
                except ValueError:
                    pass # No se encontró una coincidencia exacta, se mantiene default_index = 0
            elif len(filtered_options) == 1:
                # Si solo hay una sugerencia, pre-seleccionar esa
                default_index = display_options.index(filtered_options[0]) if filtered_options[0] in display_options else 0


            # La key del selectbox debe ser única
            suggestion_selection = st.selectbox(
                f"Sugerencias para {label}",
                options=display_options,
                index=default_index,
                key=f"{label}_suggestion_{form_key_suffix}"
            )

            # Si el usuario selecciona una sugerencia (y no es la opción vacía), usar esa.
            if suggestion_selection:
                selected_suggestion = suggestion_selection
            else:
                # Si la sugerencia se vació o no se seleccionó, usar el valor del text_input
                selected_suggestion = text_input_value

    return selected_suggestion
