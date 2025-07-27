import streamlit as st

def login_form():
    st.title("Acceso Restringido 🔒")
    st.write("Por favor, inicia sesión para acceder a la aplicación.")

    # El botón de inicio de sesión de Streamlit para OIDC
    if st.button("Iniciar Sesión con Google", key="login_button_page"):
        st.login() # Esto redirigirá al usuario a la página de login de Google