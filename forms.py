import streamlit as st
import functions as f
import pandas as pd
import datetime
class ItemForm():
    def __init__(self, formType, title, buttonName):
        list_items = []
        # Load articles for suggestions if in search mode (or submit if needed for validation)
        try:
            db_articulos = f.obtainTable('Articulos')
            if not db_articulos.empty and 'Articulo' in db_articulos.columns:
                list_items = (db_articulos['Articulo'].unique()).tolist()
                list_items.sort()
                placeholder_items = ['-Selecciona Un Artículo-']+ list_items
        except Exception as e:
            st.warning(f"No se pudieron cargar artículos para sugerencias: {e}")


        # Initialize session state variables for search form inputs
        if formType == 'search':
            if 'item_search_articulo_value' not in st.session_state :
                st.session_state[f'item_search_articulo_value'] = ''
            if 'item_search_descripcion_value' not in st.session_state:
                st.session_state[f'item_search_descripcion_value'] = ''

        # For submit form, ensure inputs are cleared on reset or reloaded from session state
        elif formType == 'submit':
                st.session_state.item_submit_articulo_value = ''
                st.session_state.item_submit_descripcion_value = ''


        # --- Form Definition ---
        with st.form(key=f'item-form-{formType}', clear_on_submit=True):
            st.write(title)

            if formType == 'submit':
                # Input fields for submission form
                # Use st.text_input directly for submission, as autocomplete might not be strictly needed here,
                # or use the simplified f.autocomplete_text_input if hints are desired.
                self.item = st.text_input(
                    'Articulo', 
                    key=f'item_submit_articulo_{formType}'
                )
                self.desc = st.text_input(
                    'Descripcion', 
                    key=f'item_submit_descripcion_{formType}'
                )
                
                # Buttons for submission form
                col_buttons_submit = st.columns(2)
                with col_buttons_submit[0]:
                    self.Button = st.form_submit_button(buttonName)

            else: # formType == 'search'
                # Input fields for search form
                # Ahora usamos la versión revisada de f.autocomplete_text_input
                self.item = st.selectbox(
                    'Articulo', 
                    placeholder_items, # Lista de todas las opciones para sugerencias
                    key=f'item_search_articulo_{formType}'
                )
                self.desc = st.text_input(
                    'Descripcion', 
                    key=f'item_search_descripcion_{formType}', 
                )

                # Buttons for search form
                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')

                # Update session state after search form interaction
                if self.ButtonReset:
                    pass
                else:
                    st.session_state[f'item_search_articulo_value'] = self.item
                    st.session_state[f'item_search_descripcion_value'] = self.desc



class CustomerForm():
    def __init__(self, formType, title, buttonName):
        list_customers = []
        # Load customers for suggestions
        try:
            db_clientes = f.obtainTable('Clientes')
            if not db_clientes.empty and 'Nombre' in db_clientes.columns:
                list_customers = (db_clientes['Nombre'].unique()).tolist()
                list_customers.sort()
                placeholder_costumers=['-Selecciona Un Cliente-']+list_customers
        except Exception as e:
            st.warning(f"No se pudieron cargar clientes para sugerencias: {e}")

        # Initialize session state variables for search form inputs
        if formType == 'search':
            if f'customer_search_name_value' not in st.session_state:
                st.session_state[f'customer_search_name_value'] = ''
            if f'customer_search_description_value' not in st.session_state:
                st.session_state[f'customer_search_description_value'] = ''
            if f'customer_search_phone_value' not in st.session_state:
                st.session_state[f'customer_search_phone_value'] = ''


        # For submit form, ensure inputs are cleared on reset or reloaded from session state
        elif formType == 'submit':
                st.session_state.customer_submit_name_value = ''
                st.session_state.customer_submit_description_value = ''
                st.session_state.customer_submit_phone_value = ''

        # --- Form Definition ---
        with st.form(key=f'customer-form-{formType}', clear_on_submit=True):
            st.write(title)

            if formType == 'submit':
                # Input fields for submission form
                self.name = st.text_input(
                    'Nombre', 
                    key=f'customer_submit_name_{formType}'
                )
                self.description = st.text_input(
                    'Descripcion', 
                    key=f'customer_submit_description_{formType}'
                )
                self.phone = st.text_input(
                    'Telefono', 
                    key=f'customer_submit_phone_{formType}'
                )
                
                # Buttons for submission form
                col_buttons_submit = st.columns(2)
                with col_buttons_submit[0]:
                    self.Button = st.form_submit_button(buttonName)


            else: # formType == 'search'
                # Input fields for search form
                self.name = st.selectbox( # Usar autocomplete para clientes también
                    'Nombre', 
                    placeholder_costumers, # Lista de todas las opciones para sugerencias
                    key=f'customer_search_name_{formType}'
                )
                self.description = st.text_input(
                    'Descripcion', 
                    key=f'customer_search_description_{formType}',
                )
                self.phone = st.text_input(
                    'Telefono',
                    key=f'customer_search_phone_{formType}',
                )

                # Buttons for search form
                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')

                # Update session state after search form interaction
                if self.ButtonReset:
                    pass
                else:
                    st.session_state[f'customer_search_name_value'] = self.name
                    st.session_state[f'customer_search_description_value'] = self.description
                    st.session_state[f'customer_search_phone_value'] = self.phone


class OrderForm():
    def __init__(self, formType, title, buttonName, list_items=None, list_customers=None):
        if list_items is None: list_items = []
        if list_customers is None: list_customers = []
        
        # --- Strict Initialization of Session State Variables for the Insertion (Submit) Form ---
        # Initialize with today's date if not already set, otherwise use existing state
        # NOTA: Estas inicializaciones solo deben ocurrir si la clave NO EXISTE o si se ha activado un RESET
        if formType =='search':
            # --- Initialization of Session State Variables for the Search Form ---
            # Estas inicializaciones no necesitan 'reset_triggered' porque se manejan con ButtonReset o con el valor por defecto
            if f'search_entrega_cliente_value' not in st.session_state: 
                st.session_state.search_entrega_cliente_value = None
            if f'search_customer_value' not in st.session_state: 
                st.session_state.search_customer_value = list_customers[0]
            if f'search_item_value' not in st.session_state: 
                st.session_state.search_item_value = list_items[0]
            if f'search_proveedor_value' not in st.session_state: 
                st.session_state.search_proveedor_value = "" 
            if f'search_pagado_value' not in st.session_state: 
                st.session_state.search_pagado_value = "" 
            if f'search_limite_value' not in st.session_state: 
                st.session_state.search_limite_value = None
            if f'search_entrega_proveedor_value' not in st.session_state: 
                st.session_state.search_entrega_proveedor_value = None
            if f'search_recogida_proveedor_value' not in st.session_state: 
                st.session_state.search_recogida_proveedor_value = None
            if f'search_recogida_cliente_value' not in st.session_state: 
                st.session_state.search_recogida_cliente_value = None
            


        elif formType == 'submit':

            if 'submit_entrega_cliente_input_key' not in st.session_state:
                st.session_state.submit_entrega_cliente_input_key = datetime.date.today()

            if 'submit_customer_selectbox_key_input' not in st.session_state: 
                st.session_state.submit_customer_selectbox_key_input = list_customers[0]
            if 'submit_item_selectbox_key_input' not in st.session_state: 
                st.session_state.submit_item_selectbox_key_input = list_items[0]
            if 'submit_descripcion_input_key' not in st.session_state: 
                st.session_state.submit_descripcion_input_key = "" 
            if 'submit_cantidad_input_key' not in st.session_state: 
                st.session_state.submit_cantidad_input_key = 1.0
            if 'submit_proveedor_selectbox_key' not in st.session_state:
                st.session_state.submit_proveedor_selectbox_key = "" 
            if 'submit_pagado_selectbox_key' not in st.session_state:
                st.session_state.submit_pagado_selectbox_key = "No Pagado" 
            if 'submit_limite_input_key' not in st.session_state: # No default to today for 'Limite'
                st.session_state.submit_limite_input_key = None 


        # Main form logic
        # Set clear_on_submit to False and handle clearing manually with a reset button
        # This prevents the form from clearing on *every* rerun or when validation fails
        with st.form(key=f'order-form-{formType}', clear_on_submit= True):#((formType == 'submit' or formType == 'search') and st.session_state.get('reset_triggered_for_order_submit', False))): # Adjusted clear_on_submit logic
            st.write(title)
            
            if formType == 'submit':
                proveedor_options = ["", "Alicia", "Dani", "Manuela", "Mari", "Marlen","M.Antonia", "Marta"]
                pagado_options = ["No Pagado", "Efectivo", "Tarjeta", "Bizum"] 

                col1submit, col2submit = st.columns(2)

                with col1submit:
                    self.entregaCliente = st.date_input(
                        'Entrega_Cliente', 
                        format="DD/MM/YYYY", 
                        key='submit_entrega_cliente_input_key' # Clave de session_state para este widget
                    )

                    self.customer = st.selectbox(
                        'Cliente', 
                        list_customers, 
                        key='submit_customer_selectbox_key_input' 
                    )
                    self.item = st.selectbox(
                        'Articulo', 
                        list_items, 
                        key='submit_item_selectbox_key_input' 
                    )
                    
                    self.desc = st.text_input(
                        'Descripcion', 
                        key='submit_descripcion_input_key'
                    )

                with col2submit:
                    self.quantity = st.number_input(
                        'Cantidad', 
                        step=1.0, 
                        key='submit_cantidad_input_key'
                    )

                    current_supplier_index = 0
                    if st.session_state.submit_proveedor_selectbox_key in proveedor_options:
                        current_supplier_index = proveedor_options.index(st.session_state.submit_proveedor_selectbox_key)
                    
                    self.supplier = st.selectbox(
                        'Proveedor', 
                        proveedor_options, 
                        index=current_supplier_index,
                        key='submit_proveedor_selectbox_key'
                    )
                    
                    current_paid_index = 0
                    if st.session_state.submit_pagado_selectbox_key in pagado_options:
                        current_paid_index = pagado_options.index(st.session_state.submit_pagado_selectbox_key)

                    self.paid = st.selectbox(
                        'Pagado', 
                        pagado_options, 
                        index=current_paid_index,
                        key='submit_pagado_selectbox_key'
                    )

                    self.limit = st.date_input(
                        'Limite', 
                        format="DD/MM/YYYY", 
                        key='submit_limite_input_key'
                    )
                
                # Buttons for submission form
                col_buttons = st.columns(2)
                with col_buttons[0]:
                    self.Button = st.form_submit_button(buttonName) 


            else:   ##SEARCH
                proveedor_options = ["", "Alicia", "Dani", "Manuela", "Mari", "Marlen","M.Antonia", "Marta"]
                pagado_options = ["", "No Pagado", "Efectivo", "Tarjeta", "Bizum"]

                col1search,col2search = st.columns(2)

                with col1search:
                    # Input fields for search form
                    self.deliveryDate = st.date_input(
                        'Entrega_Cliente', 
                        value=st.session_state.search_entrega_cliente_value, 
                        format="DD/MM/YYYY", 
                        key='search_entrega_cliente_key'
                    )
                    self.customer = st.selectbox(
                        'Cliente', 
                        list_customers, 
                        key='search_customer_key'
                    )
                    self.item = st.selectbox(
                        'Articulo', 
                        list_items, 
                        key='search_item_key'
                    )

                    current_search_supplier_index = 0
                    if st.session_state.search_proveedor_value in proveedor_options:
                        current_search_supplier_index = proveedor_options.index(st.session_state.search_proveedor_value)

                    self.supplier = st.selectbox(
                        'Proveedor', 
                        proveedor_options,
                        index=current_search_supplier_index,
                        key='search_proveedor_key'
                    )
                    current_search_paid_index = 0
                    if st.session_state.search_pagado_value in pagado_options:
                        current_search_paid_index = pagado_options.index(st.session_state.search_pagado_value)

                    self.paid = st.selectbox(
                        'Pagado', 
                        pagado_options,
                        index=current_search_paid_index,
                        key='search_pagado_key'
                    )

                with col2search:


                    self.limit = st.date_input(
                        'Limite', 
                        value=st.session_state.search_limite_value, 
                        format="DD/MM/YYYY", 
                        key='search_limite_key'
                    )
                    
                    self.entrega_proveedor = st.date_input(
                        'Entrega Proveedor', 
                        value=st.session_state.search_entrega_proveedor_value, 
                        format="DD/MM/YYYY", 
                        key='search_entrega_proveedor_key'
                    )
                    self.recogida_proveedor = st.date_input(
                        'Recogida Proveedor', 
                        value=st.session_state.search_recogida_proveedor_value, 
                        format="DD/MM/YYYY", 
                        key='search_recogida_proveedor_key'
                    )
                    self.recogida_cliente = st.date_input(
                        'Recogida Cliente', 
                        value=st.session_state.search_recogida_cliente_value, 
                        format="DD/MM/YYYY", 
                        key='search_recogida_cliente_key'
                    )

                # Buttons for search form
                searchbuttons = st.columns(2)
                with searchbuttons[0]:
                    self.Button = st.form_submit_button(buttonName) 
                with searchbuttons[1]:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')

                # Handle Search Form Session State Updates (moved from outside form)
                if self.ButtonReset:
                    pass
                
                else: # Only update if submit button was pressed and not reset

                    #if not st.session_state.get('reset_triggered_for_order_search', False):
                        st.session_state.search_entrega_cliente_value = self.deliveryDate
                        st.session_state.search_customer_value = self.customer
                        st.session_state.search_item_value = self.item
                        st.session_state.search_proveedor_value = self.supplier
                        st.session_state.search_pagado_value = self.paid
                        st.session_state.search_limite_value = self.limit
                        st.session_state.search_entrega_proveedor_value = self.entrega_proveedor
                        st.session_state.search_recogida_proveedor_value = self.recogida_proveedor
                        st.session_state.search_recogida_cliente_value = self.recogida_cliente

