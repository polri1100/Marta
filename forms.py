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
                self.cost = st.number_input('Coste Sugerido', min_value=0, max_value=None)
                self.price = st.number_input('Precio Sugerido', min_value=0, max_value=None)
                self.Button = st.form_submit_button(buttonName)
            else:
                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar busqueda')
               
            

class CustomerForm():
    def __init__(self, formType, title, buttonName):
        with st.form(key='item-form-{}'.format(formType)):
            self.title = st.write(title)
            self.name = st.text_input('Nombre')
            self.desc = st.text_input('Descripción')
            self.phone = st.text_input('Telefono')

            if formType == 'submit':
                self.Button = st.form_submit_button(buttonName)
            else:
                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar busqueda')



class OrderForm():
    def __init__(self, formType, title, buttonName, list_items=None, list_customers=None, db_articulos=None):
        with st.form(key='item-form-{}'.format(formType)):
            st.write(title)

            if formType == 'submit':
                col1submit, col2submit = st.columns(2)
                with col1submit:
                    self.deliveryDate = st.date_input('Fecha Entrega', format="DD/MM/YYYY")
                    self.customer = st.selectbox('Cliente', (list_customers))
                    self.item = st.selectbox('Articulo', (list_items))
                    self.desc = st.text_input('Descripción')
                    self.quantity = st.number_input('Cantidad', min_value=0, max_value=None, step=1)
                    
                    self.Button = st.form_submit_button(buttonName)
                
                with col2submit:
                    self.suggestedButton = st.form_submit_button('Ver precios sugeridos')

                    if self.suggestedButton:

                        self.cost = st.number_input('Coste', min_value=0, max_value=None, value=db_articulos.loc[db_articulos['Articulo'] == self.item, 'Coste Sugerido'].iat[0])
                        self.price = st.number_input('Precio', min_value=0, max_value=None, value=db_articulos.loc[db_articulos['Articulo'] == self.item, 'Precio Sugerido'].iat[0])

                    else:
                        self.cost = st.number_input('Coste', min_value=0, max_value=None, value = 0)
                        self.price = st.number_input('Precio', min_value=0, max_value=None, value = 0)                   
                    self.pickUpDate = st.date_input('Fecha Recogida', None, format="DD/MM/YYYY")
                    self.payed = st.selectbox('Pagado?', ('Pagado', 'No pagado'))
                    
                    if self.payed == 'Pagado':
                        self.payed = True
                    else:
                        self.payed = False
                    


            else:
                self.deliveryDate = st.date_input('Fecha Entrega', value=None, format="DD/MM/YYYY")
                self.customer = st.text_input('Cliente')
                self.item = st.text_input('Articulo')
                self.desc = st.text_input('Descripción')
                self.pickUpDate = st.date_input('Fecha Recogida', None, format="DD/MM/YYYY")        
                self.payed = st.selectbox('Pagado?', ('','Pagado', 'No pagado'))
                
                if self.payed == 'Pagado':
                    self.payed = True
                elif self.payed == 'No pagado':
                    self.payed = False
                else:
                    self.payed = ' '
                    #de esta manera no entra en la searchFunction

                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar busqueda')


            





