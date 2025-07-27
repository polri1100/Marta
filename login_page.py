import streamlit as st

def login_form():

    col1, col2, col3 = st.columns([1, 2, 1]) 

    with col2:
        st.title("Acceso Restringido 🔒")
        st.write("Por favor, inicia sesión para acceder a la aplicación.")

        # El botón de inicio de sesión de Streamlit para OIDC
        if st.button("Iniciar Sesión con Google", key="login_button_page"):
            st.login() # Esto redirigirá al usuario a la página de login de Google