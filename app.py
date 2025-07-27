import streamlit as st
import pandas as pd 
from login_page import login_form
from home_page import home_content



# --- CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(layout="wide",
                   page_title='EL LOCAL DE MARTA',
                   page_icon='👚')

# --- DEFINICIÓN DE LAS PÁGINAS PARA ST.NAVIGATION ---

# La página de login (siempre visible cuando no está logueado)
login_page = st.Page(login_form, title="Iniciar Sesión", icon=":material/login:")

# La página de portada (la página por defecto una vez logueado)
# Nota: La función home_content es lo que se llamará al seleccionar esta página
home_page = st.Page(home_content, title="Portada", icon="👚", default=True)

# La página de logout (un "botón" de navegación)
def logout_function():
    st.logout()
    st.session_state.logged_in = False # Asegúrate de que el estado de login también se resetea
    st.rerun() # Para forzar la recarga a la pantalla de login

logout_page = st.Page(logout_function, title="Cerrar Sesión", icon=":material/logout:")

# Define tus páginas protegidas (las que están en la carpeta 'pages/')
# Asegúrate de que los nombres de los archivos en 'pages/' coincidan
articulos_page = st.Page("pages/articulos.py", title="Artículos", icon=":material/inventory_2:")
clientes_page = st.Page("pages/clientes.py",title ="Clientes", icon=":material/person_2:" )
buscar_pedidos_page = st.Page("pages/buscar_pedidos.py",title="Buscar Pedidos",icon="🔍")
insertar_pedidos_page = st.Page("pages/insertar_pedidos.py",title="Insertar Pedidos",icon="➕")



# --- LÓGICA DE NAVEGACIÓN BASADA EN EL ESTADO DE LOGIN ---
# Usamos st.user.is_logged_in para controlar la navegación
# Puedes inicializar st.session_state.logged_in para tener un control más explícito si quieres,
# pero st.user.is_logged_in es el estado oficial de st.login().

if st.user.is_logged_in:
    # Si está logueado, muestra el menú completo de navegación
    pg = st.navigation(
        {
            "Principal": [home_page], # Puedes agrupar la Portada en una sección
            "Gestión": [articulos_page,clientes_page,buscar_pedidos_page,insertar_pedidos_page], # Aquí irían tus otras páginas protegidas
            # "Gestión": [articulos_page, pedidos_page, clientes_page], # Ejemplo con más páginas
            "Cuenta": [logout_page], # La opción de cerrar sesión
        }
    )
else:
    # Si NO está logueado, solo muestra la página de login
    pg = st.navigation([login_page])

# Ejecuta la navegación
pg.run()