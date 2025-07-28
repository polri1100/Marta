import streamlit as st

def login_form():
    st.markdown(
        """
        <style>

        /* Elimina el padding lateral de la página para que el centrado sea más efectivo */
        .main {
            padding-left: 0rem;
            padding-right: 0rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

        # Aplicamos CSS a este contenedor para centrado vertical y horizontal
    st.markdown(
            """
            <style>
            /* Apuntamos al contenedor generado por st.columns */
            [data-testid="stVerticalBlock"] {
                display: flex;
                flex-direction: column;
                justify-content: center; /* Centra verticalmente */
                align-items: center; /* Centra horizontalmente */
                height: 50vh; /* Asegura que el contenedor tenga la altura completa del viewport */
                text-align: center; /* Centra texto dentro del bloque */
            }
            /* Ajustes para el título y texto si no se centran bien */
            h1, p {
                text-align: center;
                width: 100%; /* Asegura que el texto ocupe todo el ancho para centrado */
            }
            </style>
            """,
            unsafe_allow_html=True
        )

    st.title("Acceso Restringido 🔒", anchor=False)
    st.write("Por favor, inicia sesión para acceder a la aplicación.")
        
        # Opcional: Contenedor para el botón si quieres darle un borde o estilo visual aparte
    #with st.container(border=True): # Añadir un borde visual al botón y su texto
    st.write("") # Espacio
            # El botón de inicio de sesión
    if st.button("Iniciar Sesión con Google", key="login_button_page"):#, use_container_width=True):
        st.login() # Esto redirigirá al usuario a la página de login de Google
    st.write("") # Espacio