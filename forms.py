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
        # Las listas para sugerencias se cargan solo si es un formulario de búsqueda
        list_items = []
        if formType == 'search':
            try:
                db_articulos = f.obtainTable('articulos')
                list_items = db_articulos['Articulo'].unique().tolist()
            except Exception as e:
                st.warning(f"No se pudieron cargar artículos para sugerencias: {e}")

        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            st.write(title) # Esto está bien, se renderiza una vez

            if formType == 'submit':
                # Solo estos widgets para el formulario de SUBMIT
                item_input = st.text_input('Articulo')
                desc_input = st.text_input('Descripción')
                self.item = item_input.lower()
                self.desc = desc_input.lower()

                self.cost = st.number_input('Coste Sugerido', min_value=0.0, max_value=None, value=0.0)
                self.price = st.number_input('Precio Sugerido', min_value=0.0, max_value=None, value=0.0)
                self.Button = st.form_submit_button(buttonName)
            else: # formType == 'search'
                # Solo estos widgets para el formulario de SEARCH
                self.item = f.autocomplete_text_input('Articulo', '', list_items, f'item_search')
                # La descripción de búsqueda también debería ser autocompletado si hay una lista de descripciones comunes,
                # de lo contrario, st.text_input es suficiente. Por ahora, lo dejo como text_input simple
                self.desc = st.text_input('Descripción').lower()

                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar busqueda')
                
            

class CustomerForm():
    def __init__(self, formType, title, buttonName):
        list_customers = []
        if formType == 'search':
            try:
                db_clientes = f.obtainTable('clientes')
                list_customers = db_clientes['Nombre'].unique().tolist()
            except Exception as e:
                st.warning(f"No se pudieron cargar clientes para sugerencias: {e}")

        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            st.write(title) # Esto está bien

            if formType == 'submit':
                # Solo estos widgets para el formulario de SUBMIT
                name_input = st.text_input('Nombre')
                desc_input = st.text_input('Descripción')
                phone_input = st.text_input('Telefono')

                self.name = name_input.lower()
                self.desc = desc_input.lower()
                self.phone = phone_input

                self.Button = st.form_submit_button(buttonName)
            else: # formType == 'search'
                # Solo estos widgets para el formulario de SEARCH
                self.name = f.autocomplete_text_input('Nombre', '', list_customers, f'customer_search')
                self.desc = st.text_input('Descripción').lower() # Dejar como text_input simple si no hay lista de sugerencias para descripciones
                self.phone = st.text_input('Telefono') # Teléfono rara vez necesita autocompletado predictivo.

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

                    # Estos son selectbox, ya tienen su propia función de búsqueda/filtro
                    customer_selected = st.selectbox('Cliente', (list_customers))
                    item_selected = st.selectbox('Articulo', (list_items))
                    
                    desc_input = st.text_input('Descripción') # Podría ser autocompletado si hay descripciones comunes.

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
                                default_cost_value = float(filtered_article['Coste Sugerido'].iloc[0])
                                default_price_value = float(filtered_article['Precio Sugerido'].iloc[0])
                        except Exception as e:
                            st.warning(f"Error al obtener precios sugeridos: {e}. Asegúrate de que las columnas 'Coste Sugerido' y 'Precio Sugerido' existen y que el artículo seleccionado es válido.")


                    self.cost = st.number_input('Coste', min_value=0.0, max_value=None, value=default_cost_value)
                    self.price = st.number_input('Precio', min_value=0.0, max_value=None, value=default_price_value)

                    self.pickUpDate = st.date_input('Fecha Recogida', None, format="DD/MM/YYYY")
                    payed_selection = st.selectbox('Pagado', ('No pagado', 'Pagado'))

                    if payed_selection == 'Pagado':
                        self.payed = True
                    else:
                        self.payed = False

                    self.Button = st.form_submit_button(buttonName)


            else: # formType == 'search'
                # Estos son los widgets para el formulario de SEARCH
                self.deliveryDate = st.date_input('Fecha Entrega', value=None, format="DD/MM/YYYY")

                # Aquí se usan los autocompletados
                self.customer = f.autocomplete_text_input('Cliente', '', list_customers, f'order_search_customer')
                self.item = f.autocomplete_text_input('Articulo', '', list_items, f'order_search_item')
                
                desc_input = st.text_input('Descripción')
                self.desc = desc_input.lower() # Puedes hacer esto autocompletado si hay descripciones comunes

                self.pickUpDate = st.date_input('Fecha Recogida', None, format="DD/MM/YYYY")
                
                payed_selection = st.selectbox('Pagado', ('','Pagado', 'No pagado'))

                if payed_selection == 'Pagado':
                    self.payed = True
                elif payed_selection == 'No pagado':
                    self.payed = False
                else:
                    self.payed = ' '

                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar busqueda')