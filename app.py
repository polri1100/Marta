import streamlit as st
import pandas as pd 


# --- CONFIGURACIÓN INICIAL DE LA PÁGINA ---
st.set_page_config(layout="wide",
                   page_title='EL LOCAL DE MARTA',
                   page_icon='👚')

# --- LÓGICA DE AUTENTICACIÓN CON ST.LOGIN() ---

# st.user es un objeto que contiene información del usuario si está logueado.
# st.user.is_logged_in es True si el usuario ha iniciado sesión.
if not st.user.is_logged_in:
    st.title("Acceso Restringido 🔒")
    st.write("Por favor, inicia sesión para acceder a la aplicación.")
    
    # --- CSS PARA OCULTAR LA BARRA LATERAL CUANDO NO ESTÁ AUTENTICADO ---
    st.markdown(
        """
        <style>
        section.main[data-testid="stSidebar"] {
            display: none !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # El botón de inicio de sesión de Streamlit para OIDC
    # No necesitamos un input de contraseña, Streamlit redirige al proveedor.
    # No es necesario envolverlo en un st.form()
    if st.button("Iniciar Sesión con Google", key="login_button"):
        st.login() # Esto redirigirá al usuario a la página de login de Google

    st.stop() # Detiene la ejecución si no está logueado
    
# --- CONTENIDO DE LA PORTADA (SOLO SE MUESTRA SI st.user.is_logged_in es True) ---
# Si llegamos aquí, el usuario ya ha iniciado sesión. La barra lateral se mostrará.

st.markdown("# EL LOCAL DE MARTA 👚")
st.sidebar.markdown("# Portada 👚") # Esto aparece en la barra lateral una vez logueado
st.write(f"¡Bienvenida, {st.user.name} a la aplicación de gestión de tu negocio!") # st.user.name tendrá el nombre del usuario logueado
st.write("Selecciona una opción para empezar:")

# Botón para cerrar sesión (en la barra lateral)
if st.sidebar.button("Cerrar Sesión", key="logout_button_sidebar"):
    st.logout() # Esto cierra la sesión OIDC
    st.rerun() # Para forzar la recarga a la pantalla de login

st.markdown("---")
st.subheader("Navegación Principal")

st.info("Para navegar a otras secciones (Artículos, Pedidos, etc.), usa los enlaces en la barra lateral izquierda.")
st.write("Ahora que has iniciado sesión, puedes acceder a todas las secciones de la aplicación.")
st.markdown("---")
st.write("Contenido adicional de la portada aquí.")

# La función app_main() ya no es necesaria con esta estructura.
# El código se ejecuta de arriba abajo.