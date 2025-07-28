import streamlit as st
import pandas as pd 
from login_page import login_form
from home_page import home_content



# --- CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(layout="wide",
                   page_title='EL TALLER DE MARTA',
                   page_icon='👚')

# --- LÓGICA DE AUTENTICACIÓN CON ST.LOGIN() Y VERIFICACIÓN DE ACCESO ---

# Obtener la lista de correos autorizados desde secrets.toml
# Asegúrate de que el 'emails' en secrets.toml esté configurado como una lista de strings
try:
    AUTHORIZED_EMAILS = st.secrets["authorized_users"]["emails"]
except KeyError:
    st.error("Error: La lista de correos autorizados no está configurada en secrets.toml.")
    st.stop()


# Verificar si el usuario está logueado Y si su correo está autorizado
# st.session_state.is_authorized será nuestro propio indicador de autorización
if 'is_authorized' not in st.session_state:
    st.session_state.is_authorized = False

if st.user.is_logged_in:
    # Si el usuario está logueado con Google, verificamos su email
    if st.user.email in AUTHORIZED_EMAILS:
        st.session_state.is_authorized = True
    else:
        # Si el email no está autorizado, cerramos la sesión de Google
        # y marcamos como no autorizado
        st.error(f"Acceso denegado: El correo '{st.user.email}' no está autorizado para usar esta aplicación.")
        st.session_state.is_authorized = False
        st.logout() # Cierra la sesión de Google
        #st.rerun() # Fuerza una recarga para mostrar la pantalla de login de nuevo
else:
    # Si no está logueado en absoluto, marcamos como no autorizado
    st.session_state.is_authorized = False


# --- DEFINICIÓN DE LAS PÁGINAS PARA ST.NAVIGATION ---

# La página de login (siempre visible cuando no está logueado)
login_page = st.Page(login_form, title="Iniciar Sesión", icon=":material/login:")

# La página de portada (la página por defecto una vez logueado)
# Nota: La función home_content es lo que se llamará al seleccionar esta página
home_page = st.Page(home_content, title="Inicio", icon=":material/home:", default=True)

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
buscar_pedidos_page = st.Page("pages/buscar_pedidos.py",title="Buscar Pedidos",icon=":material/search:")
insertar_pedidos_page = st.Page("pages/insertar_pedidos.py",title="Insertar Pedidos",icon=":material/add:")



# --- LÓGICA DE NAVEGACIÓN BASADA EN EL ESTADO DE LOGIN ---

if st.user.is_logged_in:
    # Si está logueado, muestra el menú completo de navegación
    pg = st.navigation(
        {
            "Principal": [home_page], # Puedes agrupar la Portada en una sección
            "Gestión": [articulos_page,clientes_page,buscar_pedidos_page,insertar_pedidos_page], # Aquí irían tus otras páginas protegidas
            "Cuenta": [logout_page], # La opción de cerrar sesión
        }
    )
else:
    # Si NO está logueado, solo muestra la página de login
    pg = st.navigation([login_page])

# Ejecuta la navegación
pg.run()
