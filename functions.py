import pygsheets
import pandas as pd
import streamlit as st
import datetime
import json

def obtainSheet(sheetName):

    secrets = '{"type": "service_account", "project_id": "martacostura", "private_key_id": "fce6e0f0d0d4688261fd3f40b6fba53e87089c3d", "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDB9OSC+qecw0fM\nSCwvtb2csdpSQS/Pgw+qNSHG7lGsegFDiYz6JcD5WIoKqu96iuQTv3bJIPfyQ19i\n8jXPLjjX9NPhKTNdisQxT2mRNfW3KZzEAd+PNySKtS/KBy+4AOV1zAumR2NMM5I5\nCA/MFWnO9I3lSXzEZjWpdX+AjSYYzsOep3Vy1g5ZMtcGmjuHAp+Nk44LtF2bcpys\nzQwoDuZoQkaNm8kd8WRP3cfPvru/usyzCGTnStbCHFfBnxqOnZ037cYzCXoOmL7E\n4GuFk5vznRXmCC69mm/pUYU9Q7KRD99xYZFl/9hD57233HVCoi/gR6YjJPwH/MCp\nqBBBklsXAgMBAAECggEADux7ng27UoyUEbExSoUpZHfVh063Zw176b981y8Eicjk\nIADiyryXme1Tcc6v7os7/BOsstJz7D19hsIsRxdqDZ6A+b+PJuYZLSd3GqfpktZY\n1vFt9ORr+LWdn7s902Ko7+TAtg1NeVIz22o2DPX41jvAT0wq6tG9KfTTLV5Zor7j\nrqelH7RAF/XSO/dXfBko0KRylquGu/kC4uJcURsZT9K6xAbwI28lMufl88iXEXE0\nRRuKVrDTsvko2jiBz0UDScb1ELf39THnvRH45e7hcQFi72sm/Jzo8gBXE6M+6aha\noGmmHngqYWArd1302ubpSOBphGatS5iW/n62Di8fAQKBgQDw2EusdElpmuv6qD+u\ndFxYOqElQO/jJY5a1rNOJWpBp/c7UEow9oi0s6J/6akYcdy1X7CdIvBOZiAzCjry\nYYBP/+35rz4Xbk+nqzOPj4qeLtuhnSVSFYHNpJoPCXo/FgworS4Dn6nI4S/tQ5iK\nljAzViRNjmyPQwb2NxgXkHYgUQKBgQDOKUlRN76butziPAXmYhVyAxPRr+xGotme\nx1lGbkxjwbZnFsjr98rNj2H0lvZbLgo0hH6pduRckxugr721QGXerR9ml3CDIB+M\nqRbT+oOKS/1/WEfvWckFJlOiIjSKhEHn3qdgasW0MqoqgQ3SZbjY8ihebbi+sXAK\nhx74cX2S5wKBgCiGDD2JF20Ybwou0wA0ffEudDzDb1mF0S0BoQvOCdHgRB4LxV/1\nq0zUSMxC8Xu2dM9juWDHJy3ZyyMrXn234BIV2uG/FbB1lBt/F97Y5Rb2hWfs/AGS\nstN6FZ3gF1yUBhm2Ad8EN1ogYaMHU5xF5vhMTzFpfGSif4JgBMK6QNXxAoGAb1b4\n07YpaO14UW5dOVkLf/GNiJdcIaHdqdS7sD/tXYrGudIiXN4MVwvyuSe2kPPCay6L\nQXaGSkDgkN2YtQS8f5A7/yoWh5qXr126iG0pEU2M8HN7FhcFa5SRYmTav1xCQ7mJ\n55aCg5lBMYdVMaXiOLg/eRAE0Gf/vI/Q+BhC200CgYEAsrKvJeDYp0PR5LrE18Zj\n/SNc/rh1OJjYvV9FAF+4bWQe7qaihh6gD4kKGEp4sgBp1e6kBymkEQwY3dH9G8wo\nAeGwQg9Y3dfaQZ4U+wxnuyQdPulnj/IBEn5pfesljdZklfq6nNN2243Zw72uEuYp\nZzSetL1lB9KXlcN2CBcc9oo=\n-----END PRIVATE KEY-----\n", "client_email": "marta-costura-sheets@martacostura.iam.gserviceaccount.com", "client_id": "116789383299631603165", "auth_uri": "https://accounts.google.com/o/oauth2/auth", "token_uri": "https://oauth2.googleapis.com/token", "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs", "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/marta-costura-sheets%40martacostura.iam.gserviceaccount.com", "universe_domain": "googleapis.com"}'
    client = pygsheets.authorize(service_account_file=json.loads(secrets, strict=False))

    #client = pygsheets.authorize(service_account_file=json.loads('streamlit/secrets.toml', strict=False))

    excel = client.open_by_url('https://docs.google.com/spreadsheets/d/1pz_MPwerlbM5--sAdBykbcImsRL-zNGezqLI69oX-ac/edit?usp=sharing')
    sheet = excel.worksheet_by_title(sheetName)

    return sheet

def obtainTable(sheetName):
    
    sheet = obtainSheet(sheetName)
    db = sheet.get_as_df()
    print(db)
    return db

def uploadTable(db, sheetName):

    sheet = obtainSheet(sheetName)
    sheet.resize(db.shape[0],db.shape[1])
    sheet.set_dataframe(db, start= (1,1))

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
        confirmationButton = st.button("Si! Estoy segura")

        # If confirmation button is not clicked, stop execution
        if not confirmationButton:
            return
        
        if st.session_state.deleteButton and confirmationButton:
            st.session_state.deleteButton = False
            checkunique = deleteRow(fileName, deleteNumber)
            if not checkunique:
                st.success('Borrado :)', icon="✅")


