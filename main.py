import streamlit as st
import pandas as pd 
from pathlib import Path
import os


def app_main():
    path = Path(os.getcwd()).parent.absolute() / "Marta/data/"

    st.set_page_config(layout="wide")

    st.markdown("# EL LOCAL DE MARTA 👚")
    st.sidebar.markdown("# Portada 👚")

if __name__ == '__main__':
    app_main()
