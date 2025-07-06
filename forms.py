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
        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            self.title = st.write(title)
            item_input = st.text_input('Articulo')
            desc_input = st.text_input('Descripción')
            
            self.item= item_input.lower()
            self.desc= desc_input.lower()

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
        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            self.title = st.write(title)
            name_input = st.text_input('Nombre')
            desc_input = st.text_input('Descripción')
            phone_input = st.text_input('Telefono')

            self.name = name_input.lower()
            self.desc = desc_input.lower()
            self.phone = phone_input 

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
        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            st.write(title)

            if formType == 'submit':
                col1submit, col2submit = st.columns(2)
                with col1submit:
                    self.deliveryDate = st.date_input('Fecha Entrega', format="DD/MM/YYYY")
                    customer_selected = st.selectbox('Cliente', (list_customers))
                    item_selected = st.selectbox('Articulo', (list_items))
                    desc_input = st.text_input('Descripción')

                    # Aplicar .lower() después de obtener los valores
                    self.customer = customer_selected.lower()
                    self.item = item_selected.lower()
                    self.desc = desc_input.lower()
                    self.quantity = st.number_input('Cantidad', min_value=0, max_value=None, step=1)
                    

                
                with col2submit:
                    self.suggestedButton = st.form_submit_button('Ver precios sugeridos')

                    default_cost_value = 0.0
                    default_price_value = 0.0

                    if self.suggestedButton and db_articulos is not None:
                        try:
                            filtered_article = db_articulos.loc[db_articulos['Articulo'].str.lower() == self.item]
                            if not filtered_article.empty:
                                default_cost_value = filtered_article['Coste Sugerido'].iloc[0]
                                default_price_value = filtered_article['Precio Sugerido'].iloc[0]
                        except Exception as e:
                            st.warning(f"Error al obtener precios sugeridos: {e}. Asegúrate de que las columnas 'Coste Sugerido' y 'Precio Sugerido' existen y que el artículo seleccionado es válido.")


                    self.cost = st.number_input('Coste', min_value=0.0, max_value=None, value=float(default_cost_value)) # Asegurar float
                    self.price = st.number_input('Precio', min_value=0.0, max_value=None, value=float(default_price_value)) # Asegurar float
                    
                    self.pickUpDate = st.date_input('Fecha Recogida', None, format="DD/MM/YYYY")
                    payed_selection = st.selectbox('Pagado', ('No pagado', 'Pagado'))
                    
                    if payed_selection == 'Pagado':
                        self.payed = True
                    else: 
                        self.payed = False

                    self.Button = st.form_submit_button(buttonName)
                    


            else:
                self.deliveryDate = st.date_input('Fecha Entrega', value=None, format="DD/MM/YYYY")

                customer_input = st.text_input('Cliente')
                item_input = st.text_input('Articulo')
                desc_input = st.text_input('Descripción')
                payed_selection = st.selectbox('Pagado', ('','Pagado', 'No pagado'))
                
                self.customer = customer_input.lower()
                self.item = item_input.lower()
                self.desc = desc_input.lower()

                self.pickUpDate = st.date_input('Fecha Recogida', None, format="DD/MM/YYYY")        
                
                if payed_selection == 'Pagado':
                    self.payed = True
                elif payed_selection == 'No pagado':
                    self.payed = False
                else: 
                    self.payed = ' '
                    #de esta manera no entra en la searchFunction

                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar busqueda')


            





