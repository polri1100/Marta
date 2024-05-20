import os
import pandas as pd
import streamlit as st
from streamlit_modal import Modal
import streamlit.components.v1 as components

from pathlib import Path
import datetime

def obtainPath(fileName):
    path = Path(os.getcwd()).parent.absolute() / "Marta/data/"
    path = path / str(fileName) 
    path = str(path) + ".xlsx"

    return path

def obtainTable(fileName):
    path = obtainPath(fileName)
    db = pd.read_excel(path)

    return db

def uploadTable(db, fileName):

    fileName = obtainPath(fileName)
    db.to_excel(fileName, index=False)

def displayTable(db, sortField='ID'):
    db = db.sort_values(by=[sortField], ascending=False)
    st.dataframe(db, hide_index=True, use_container_width=True)

def returnMaxMinID(db):
    max_id = db['ID'].max()
    min_id = db['ID'].min()

    return max_id, min_id

def ordersJoin(db_pedidos, db_clientes, db_articulos):
    
    db_joined = db_pedidos.merge(db_clientes, left_on='Cliente_id', right_on='ID', how='left')
    db_joined = db_joined.merge(db_articulos, left_on='Articulo_id', right_on='ID', how='left')
    db_joined = db_joined[['ID_x', 'Fecha Entrega', 
                        'Nombre',
                        'Articulo', 'Descripcion_x',
                        'Cantidad', 'Coste', 'Precio',
                        'Pagado', 'Fecha Recogida']]

    db_joined["Pagado"] = db_joined["Pagado"].astype('bool')
    db_joined["Fecha Entrega"] = db_joined["Fecha Entrega"].dt.strftime('%d/%m/%Y')
    db_joined["Fecha Recogida"] = db_joined["Fecha Recogida"].dt.strftime('%d/%m/%Y')

    db_joined.rename(columns={'ID_x': 'ID'}, inplace=True)
    db_joined.rename(columns={'Descripcion_x': 'Descripcion'}, inplace=True)


    return db_joined


def submitDatasource(new_row, fileName, uniqueColumn=None, restrictedValue=''):
    df_new = pd.DataFrame(new_row)
    df_existing = obtainTable(fileName)

    
    if new_row[uniqueColumn] == ['']:
        st.warning('El nombre no puede estar vacio', icon="⚠️")
        return df_existing
    
    try:
        repeatedValue = new_row[uniqueColumn] in df_existing[uniqueColumn].values
        st.warning('El nombre ya existe. No puede haber dos {}s iguales'.format(uniqueColumn.lower()), icon="⚠️")
        return df_existing
    except Exception:
        pass

    if len(restrictedValue) == 9 or restrictedValue == '':
        pass
    else:
        st.warning('El telefono debe contener nueve digitos', icon="⚠️")
        return df_existing

    df_combined = pd.concat([df_existing, df_new])
    uploadTable(df_combined, fileName)
    st.success('    Añadido :)', icon="✅")
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
                db = db[db[args[count]].str.contains(instAtr, na=False)]

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

def deleteForm(min_id, max_id, fileName):

    if "deleteButton" not in st.session_state:
        st.session_state.deleteButton = False

    if "confirmation" not in st.session_state:
        st.session_state.confirmation = False

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

        # css="""
        # <style>
        #     [data-testid="stForm"]:nth-child(1) {
        #         background-color: red;
        #     }
        # </style>
        # """

        # st.write(css, unsafe_allow_html=True)

    if st.session_state.deleteButton:
        st.session_state.deleteButton = True
        st.warning('Estas segura que quieres borrar? Esta opcion no se puede deshacer')
        st.session_state.confirmation = st.button("Si! Estoy segura")

        # If confirmation button is not clicked, stop execution
        if not st.session_state.confirmation:
            return
        
        if st.session_state.deleteButton and st.session_state.confirmation:
            st.session_state.deleteButton = False
            deleteRow(fileName, deleteNumber)
            st.success('Borrado :)', icon="✅")


