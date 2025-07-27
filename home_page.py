import streamlit as st

def home_content():
    st.markdown("# EL LOCAL DE MARTA 👚")
    st.write(f"¡Bienvenida, {st.user.name} a la aplicación de gestión de tu negocio!")
    st.write("Selecciona una opción para empezar:")

    st.markdown("---")
    st.subheader("Navegación Principal")

    st.info("Para navegar a otras secciones (Artículos, Pedidos, etc.), usa los enlaces en la barra lateral izquierda.")
    st.write("Ahora que has iniciado sesión, puedes acceder a todas las secciones de la aplicación.")
    st.markdown("---")
    st.write("Contenido adicional de la portada aquí.")