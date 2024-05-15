import streamlit as st
import functions as f

# class Form():
#     def __init__(self, formType, title, buttonName):
#         with st.form(key='item-form-{}'.format(formType)):
#             self.title = st.write(title)
#             self.ownForm = ItemForm()

#             self.Button = st.form_submit_button(buttonName)

#     def startForm(self, formType, title, buttonName):
#         with st.form(key='item-form-{}'.format(formType)):
#             self.title = st.write(title)
#             self.Button = st.form_submit_button(buttonName)


class ItemForm():
    def __init__(self, formType, title, buttonName, type='search'):
        with st.form(key='item-form-{}'.format(formType)):
            self.title = st.write(title)
            self.item = st.text_input('Articulo')
            self.desc = st.text_input('Descripción')
            if type == 'submit':
                self.cost = st.number_input('Coste Sugerido')
                self.price = st.number_input('Precio Sugerido')

            self.Button = st.form_submit_button(buttonName)
        # # inheriting the properties of parent class
        # super().__init__(type, title, buttonName)  

class CustomerForm():
    def __init__(self, formType, title, buttonName):
        with st.form(key='item-form-{}'.format(formType)):
            self.title = st.write(title)
            self.name = st.text_input('Nombre')
            self.phone = st.text_input('Telefono')

            self.Button = st.form_submit_button(buttonName)
        # # inheriting the properties of parent class
        # super().__init__(type, title, buttonName)  



