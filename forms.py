import streamlit as st
import functions as f
import pandas as pd

class ItemForm():
    def __init__(self, formType, title, buttonName):
        # Las listas para sugerencias se cargan solo si es un formulario de búsqueda
        list_items = []
        if formType == 'search':
            try:
                # Cargar la tabla 'Articulos' de Supabase (nombre de tabla con mayúscula inicial)
                db_articulos = f.obtainTable('Articulos')
                # Obtener la lista de Articulos para autocompletar
                # Asegúrate que la columna se llama 'Articulo' en Supabase.
                if not db_articulos.empty and 'Articulo' in db_articulos.columns:
                    list_items = db_articulos['Articulo'].unique().tolist()
                else:
                    st.warning("La tabla 'Articulos' está vacía o no tiene la columna 'Articulo'.")
            except Exception as e:
                st.warning(f"No se pudieron cargar artículos para sugerencias: {e}")

        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            st.write(title)

            if formType == 'submit':
                # Solo estos widgets para el formulario de SUBMIT
                item_input = st.text_input('Articulo')
                desc_input = st.text_input('Descripción')
                # Los atributos internos del formulario son flexibles, se mapean a los nombres de columna en articulos.py
                self.item = item_input # .lower() se aplicará en submitDatasource o antes de enviar a DB si es necesario
                self.desc = desc_input

                # Asegúrate que las etiquetas aquí son como quieres que se muestren
                # y que los nombres de columna en Supabase son 'Coste_Sugerido', 'Precio_Sugerido'
                self.cost = st.number_input('Coste Sugerido', min_value=0.0, max_value=None, value=0.0)
                self.price = st.number_input('Precio Sugerido', min_value=0.0, max_value=None, value=0.0)
                self.Button = st.form_submit_button(buttonName)
            else: # formType == 'search'
                # Solo estos widgets para el formulario de SEARCH
                # Pasa la lista de artículos cargada
                self.item = st.text_input('Articulo')
                self.desc = st.text_input('Descripción') # Puedes mantenerla sin .lower() aquí, searchFunction lo hace

                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')
                
            

class CustomerForm():
    def __init__(self, formType, title, buttonName):
        list_customers = []
        if formType == 'submit':
            try:
                # Cargar la tabla 'Clientes' de Supabase
                db_clientes = f.obtainTable('Clientes')
                # Asegúrate que la columna se llama 'Nombre' en Supabase.
                if not db_clientes.empty and 'Nombre' in db_clientes.columns:
                    list_customers = db_clientes['Nombre'].unique().tolist()
                else:
                    st.warning("La tabla 'Clientes' está vacía o no tiene la columna 'Nombre'.")
            except Exception as e:
                st.warning(f"No se pudieron cargar clientes para sugerencias: {e}")

        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            st.write(title)

            if formType == 'submit':
                self.name = st.text_input('Nombre')
                self.desc = st.text_input('Descripción')
                self.phone = st.text_input('Telefono')
                self.Button = st.form_submit_button(buttonName)

            else: # formType == 'search'
                self.name = st.text_input('Nombre', key='customer_search_name')
                self.desc = st.text_input('Descripción', key='customer_search_desc')
                self.phone = st.text_input('Telefono', key='customer_search_phone')

                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')



class OrderForm():
    def __init__(self, formType, title, buttonName, list_items=None, list_customers=None, db_articulos=None):
        if list_items is None: list_items = []
        if list_customers is None: list_customers = []
        
        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            st.write(title)

            if formType == 'submit':
                col1submit, col2submit = st.columns(2)
                with col1submit:
                    self.deliveryDate = st.date_input('Fecha_Entrega', format="DD/MM/YYYY")

                    # Estos selectbox obtendrán sus opciones de las listas pasadas desde pedidos.py
                    # Asegúrate que list_customers y list_items que pasas a OrderForm ya estén limpias
                    customer_selected = st.selectbox('Cliente', ([''] + list_customers if list_customers else [''])) # Añadir opción vacía
                    item_selected = st.selectbox('Articulo', ([''] + list_items if list_items else [''])) # Añadir opción vacía
                    
                    desc_input = st.text_input('Descripción')

                    self.customer = customer_selected # Ya no aplicamos .lower() aquí. Se hará en el submitDatasource si es necesario.
                    self.item = item_selected # Idem
                    self.desc = desc_input # Idem

                    self.quantity = st.number_input('Cantidad', min_value=0, max_value=None, step=1)

                with col2submit:
                    self.suggestedButton = st.form_submit_button('Ver precios sugeridos')

                    default_cost_value = 0.0
                    default_price_value = 0.0

                    # Lógica para obtener precios sugeridos
                    if self.suggestedButton and db_articulos is not None and self.item:
                        try:
                            # Asegúrate de que los nombres de columna aquí coinciden con Supabase: 'Articulo', 'Coste_Sugerido', 'Precio_Sugerido'
                            filtered_article = db_articulos.loc[db_articulos['Articulo'].astype(str).str.lower() == str(self.item).lower()]
                            if not filtered_article.empty:
                                # Acceder a las columnas con los nombres exactos de Supabase
                                default_cost_value = float(filtered_article['Coste_Sugerido'].iloc[0])
                                default_price_value = float(filtered_article['Precio_Sugerido'].iloc[0])
                            else:
                                st.info("Artículo no encontrado para sugerir precios.")
                        except Exception as e:
                            st.warning(f"Error al obtener precios sugeridos: {e}. Revise las columnas 'Coste_Sugerido' y 'Precio_Sugerido'.")
                    
                    self.cost = st.number_input('Coste', min_value=0.0, max_value=None, value=default_cost_value)
                    self.price = st.number_input('Precio', min_value=0.0, max_value=None, value=default_price_value)

                    self.pickUpDate = st.date_input('Fecha_Recogida', None, format="DD/MM/YYYY")
                    payed_selection = st.selectbox('Pagado', ('No pagado', 'Pagado'))

                    if payed_selection == 'Pagado':
                        self.payed = True
                    else:
                        self.payed = False

                    self.Button = st.form_submit_button(buttonName)

            else: # formType == 'search'
                self.deliveryDate = st.date_input('Fecha_Entrega', value=None, format="DD/MM/YYYY")

                # Aquí se usan los autocompletados
                # Pasa las listas de clientes/artículos para autocompletar
                self.customer = st.text_input('Cliente')
                self.item = st.text_input('Articulo')
                
                desc_input = st.text_input('Descripción')
                self.desc = desc_input # Mantener sin .lower() aquí

                self.pickUpDate = st.date_input('Fecha_Recogida', None, format="DD/MM/YYYY")
                
                payed_selection = st.selectbox('Pagado', ('','Pagado', 'No pagado'))

                if payed_selection == 'Pagado':
                    self.payed = True
                elif payed_selection == 'No pagado':
                    self.payed = False
                else: # Si se selecciona la opción vacía
                    self.payed = None # Mejor None que ' ' para bool en búsqueda

                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')