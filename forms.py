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
    def __init__(self, formType, title, buttonName):
        with st.form(key='item-form-{}'.format(formType)):
            self.title = st.write(title)
            self.item = st.text_input('Articulo')
            self.desc = st.text_input('Descripción')
            if formType == 'submit':
                self.cost = st.number_input('Coste Sugerido')
                self.price = st.number_input('Precio Sugerido')

            self.Button = st.form_submit_button(buttonName)

class CustomerForm():
    def __init__(self, formType, title, buttonName):
        with st.form(key='item-form-{}'.format(formType)):
            self.title = st.write(title)
            self.name = st.text_input('Nombre')
            self.phone = st.text_input('Telefono')

            self.Button = st.form_submit_button(buttonName)


class OrderForm():
    def __init__(self, formType, title, buttonName, list_items=None, list_customers=None, db_articulos=None):
        with st.form(key='item-form-{}'.format(formType)):
            st.write(title)

            if formType == 'submit':
                self.deliveryDate = st.date_input('Fecha Entrega', format="DD/MM/YYYY")
                self.customer = st.selectbox('Cliente', (list_customers))
                self.item = st.selectbox('Articulo', (list_items))

                self.quantity = st.number_input('Cantidad', step=1)
                self.suggestedButton = st.form_submit_button('Ver coste y precio sugeridos')

                if self.suggestedButton:

                    self.cost = st.number_input('Coste', db_articulos.loc[db_articulos['Articulo'] == self.item, 'Coste Sugerido'].iat[0])
                    self.price = st.number_input('Precio', db_articulos.loc[db_articulos['Articulo'] == self.item, 'Precio Sugerido'].iat[0])

                else:
                    self.cost = st.number_input('Coste', value = 0)
                    self.price = st.number_input('Precio', value = 0)

                self.payed = st.selectbox('Pagado?', ('Pagado', 'No pagado'))
                
                if self.payed == 'Pagado':
                    self.payed = True
                else:
                    self.payed = False

            else:
                self.deliveryDate = st.date_input('Fecha Entrega', value=None, format="DD/MM/YYYY")
                self.customer = st.text_input('Cliente')
                self.item = st.text_input('Articulo')

                self.payed = st.selectbox('Pagado?', ('','Pagado', 'No pagado'))
                
                if self.payed == 'Pagado':
                    self.payed = True
                elif self.payed == 'No pagado':
                    self.payed = False
                else:
                    self.payed = ' '
                    #de esta manera no entra en la searchFunction


            
            self.pickUpDate = st.date_input('Fecha Recogida', None, format="DD/MM/YYYY")
            self.Button = st.form_submit_button(buttonName)




