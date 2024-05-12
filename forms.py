import streamlit as st

class Form():
    def __init__(self, title):
        with st.form(key='item-form-submit'):
            self.title = st.write(title)
            self.item = st.text_input('Articulo')
            self.desc = st.text_input('Descripción')
            self.cost = st.number_input('Coste Sugerido')
            self.price = st.number_input('Precio Sugerido')
            self.submitButton = st.form_submit_button('Guardar registro')

    # def returnSubmitButton(self):
    #     submitButton = st.form_submit_button('Guardar registro')
        
    #     return submitButton 
    