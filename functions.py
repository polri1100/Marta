import os
import pandas as pd
import streamlit as st
from pathlib import Path

def obtainPath(fileName):
    path = Path(os.getcwd()).parent.absolute() / "Marta/data/"
    path = path / str(fileName) 
    path = str(path) + ".xlsx"

    return path

def obtainTable(fileName):
    path = obtainPath(fileName)
    db = pd.read_excel(path)

    return db

def displayTable(db):
    st.dataframe(db, hide_index=True, use_container_width=True)

def returnMaxMinID(db):
    max_id = db['ID'].max()
    min_id = db['ID'].min()

    return max_id, min_id

def submitDatasource(new_row, fileName, uniqueColumn=None):
    df_new = pd.DataFrame(new_row)
    df_existing = pd.read_excel(fileName)

    try:
        checkDuplicated = new_row[uniqueColumn] in df_existing[uniqueColumn].values
    except Exception:
        checkDuplicated = False
    
    if checkDuplicated:
        st.warning('El nombre ya existe. No puede haber dos {}s con el mismo nombre'.format(uniqueColumn), icon="⚠️")
    else:
        df_combined = pd.concat([df_existing, df_new])
        df_combined.to_excel(fileName, index=False)
        st.rerun()

def deleteRow(fileName, row):
    db = pd.read_excel(fileName)
    db = db[db.ID != row]
    db.to_excel(fileName, index=False)

    st.rerun()

def deleteForm(min_id, max_id, fileName):

    with st.form(key='item-form-delete'):
        st.write("Formulario para Borrar")
        deleteNumber = st.number_input('ID', min_value=min_id, max_value=max_id)
        deleteButton = st.form_submit_button('Eliminar registro')

        # css="""
        # <style>
        #     [data-testid="stForm"]:nth-child(1) {
        #         background-color: red;
        #     }
        # </style>
        # """

        # st.write(css, unsafe_allow_html=True)

    if deleteButton:
        deleteRow(fileName, deleteNumber)


