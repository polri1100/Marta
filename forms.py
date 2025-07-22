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
            if f'item_search_articulo_value' not in st.session_state:
                st.session_state[f'item_search_articulo_value'] = ''
            if f'item_search_descripcion_value' not in st.session_state:
                st.session_state[f'item_search_descripcion_value'] = ''
            if 'reset_triggered_for_item_search' not in st.session_state:
                st.session_state['reset_triggered_for_item_search'] = False

        # For submit form, ensure inputs are cleared on reset or reloaded from session state
        elif formType == 'submit':
            if 'item_submit_articulo_value' not in st.session_state or st.session_state.get('reset_triggered_for_item_submit', False):
                st.session_state.item_submit_articulo_value = ''
            if 'item_submit_descripcion_value' not in st.session_state or st.session_state.get('reset_triggered_for_item_submit', False):
                st.session_state.item_submit_descripcion_value = ''


        # --- Form Definition ---
        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'search' and not st.session_state.get('reset_triggered_for_item_submit', False))):
            st.write(title)

            if formType == 'submit':
                # Input fields for submission form
                # Use st.text_input directly for submission, as autocomplete might not be strictly needed here,
                # or use the simplified f.autocomplete_text_input if hints are desired.
                self.item = st.text_input(
                    'Articulo', 
                    value=st.session_state.item_submit_articulo_value, # Link to session state for persistence
                    key=f'item_submit_articulo_{formType}'
                )
                self.desc = st.text_input(
                    'Descripción', 
                    value=st.session_state.item_submit_descripcion_value, # Link to session state for persistence
                    key=f'item_submit_descripcion_{formType}'
                )
                
                # Buttons for submission form
                col_buttons_submit = st.columns(2)
                with col_buttons_submit[0]:
                    self.Button = st.form_submit_button(buttonName)
                with col_buttons_submit[1]:
                    self.ButtonReset = st.form_submit_button('Borrar formulario')
                    if self.ButtonReset:
                        st.session_state.item_submit_articulo_value = ''
                        st.session_state.item_submit_descripcion_value = ''
                        st.session_state['reset_triggered_for_item_submit'] = True # Set flag to trigger clear_on_submit next rerun

                # Update session state after form interaction (unless reset was just triggered)
                # This ensures values persist even if user navigates away and comes back, or if validation fails.
                if self.Button and not st.session_state.get('reset_triggered_for_item_submit', False):
                    pass
                
                # Reset the flag after processing for next run
                st.session_state['reset_triggered_for_item_submit'] = False

            else: # formType == 'search'
                # Input fields for search form
                # Ahora usamos la versión revisada de f.autocomplete_text_input
                self.item = st.selectbox(
                    'Articulo', 
                    placeholder_items, # Lista de todas las opciones para sugerencias
                    key=f'item_search_articulo_{formType}'
                )
                self.desc = st.text_input(
                    'Descripción', 
                    key=f'item_search_descripcion_{formType}', 
                    value=st.session_state.get(f'item_search_descripcion_value', '')
                )

                # Buttons for search form
                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')

                # Update session state after search form interaction
                if self.ButtonReset:
                    st.session_state[f'item_search_articulo_value'] = ''
                    st.session_state[f'item_search_descripcion_value'] = ''
                    st.session_state['reset_triggered_for_item_search'] = True
                else:
                    # Update session state values only if not a reset, and input has changed
                    # The text_input's value is already in self.item, so we just persist it
                    if not st.session_state.get('reset_triggered_for_item_search', False):
                        st.session_state[f'item_search_articulo_value'] = self.item
                        st.session_state[f'item_search_descripcion_value'] = self.desc

                st.session_state['reset_triggered_for_item_search'] = False


class CustomerForm():
    def __init__(self, formType, title, buttonName):
        list_customers = []
        # Load customers for suggestions
        try:
            db_clientes = f.obtainTable('Clientes')
            if not db_clientes.empty and 'Nombre' in db_clientes.columns:
                list_customers = (db_clientes['Nombre'].unique()).tolist()
                list_customers.sort()
                placeholder_costumers=['-Seleciona Un Cliente-']+list_customers
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
            if 'reset_triggered_for_customer_search' not in st.session_state:
                st.session_state['reset_triggered_for_customer_search'] = False

        # For submit form, ensure inputs are cleared on reset or reloaded from session state
        elif formType == 'submit':
            if 'customer_submit_name_value' not in st.session_state or st.session_state.get('reset_triggered_for_customer_submit', False):
                st.session_state.customer_submit_name_value = ''
            if 'customer_submit_desc_value' not in st.session_state or st.session_state.get('reset_triggered_for_customer_submit', False):
                st.session_state.customer_submit_desc_value = ''
            if 'customer_submit_phone_value' not in st.session_state or st.session_state.get('reset_triggered_for_customer_submit', False):
                st.session_state.customer_submit_phone_value = ''

        # --- Form Definition ---
        with st.form(key=f'customer-form-{formType}', clear_on_submit=((formType == 'submit' or formType == 'search') and not st.session_state.get('reset_triggered_for_customer_submit', False))):
            st.write(title)

            if formType == 'submit':
                # Input fields for submission form
                self.name = st.text_input(
                    'Nombre', 
                    value=st.session_state.customer_submit_name_value,
                    key=f'customer_submit_name_{formType}'
                )
                self.desc = st.text_input(
                    'Descripción', 
                    value=st.session_state.customer_submit_desc_value,
                    key=f'customer_submit_desc_{formType}'
                )
                self.phone = st.text_input(
                    'Teléfono', 
                    value=st.session_state.customer_submit_phone_value,
                    key=f'customer_submit_phone_{formType}'
                )
                
                # Buttons for submission form
                col_buttons_submit = st.columns(2)
                with col_buttons_submit[0]:
                    self.Button = st.form_submit_button(buttonName)
                with col_buttons_submit[1]:
                    self.ButtonReset = st.form_submit_button('Borrar formulario')

                    if self.ButtonReset:
                        st.session_state.customer_submit_name_value = ''
                        st.session_state.customer_submit_desc_value = ''
                        st.session_state.customer_submit_phone_value = ''
                        st.session_state['reset_triggered_for_customer_submit'] = True

                # Update session state after form interaction (unless reset was just triggered)
                if self.Button and not st.session_state.get('reset_triggered_for_customer_submit', False):
                    pass

                st.session_state['reset_triggered_for_customer_submit'] = False


            else: # formType == 'search'
                # Input fields for search form
                self.name = st.selectbox( # Usar autocomplete para clientes también
                    'Nombre', 
                    placeholder_costumers, # Lista de todas las opciones para sugerencias
                    key=f'customer_search_name_{formType}'
                )
                self.desc = st.text_input(
                    'Descripción', 
                    key=f'customer_search_desc_{formType}',
                    value=st.session_state.get(f'customer_search_desc_value', '')
                )
                self.phone = st.text_input(
                    'Teléfono',
                    key=f'customer_search_phone_{formType}',
                    value=st.session_state.get(f'customer_search_phone_value', '')
                )

                # Buttons for search form
                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')

                # Update session state after search form interaction
                if self.ButtonReset:
                    st.session_state[f'customer_search_name_value'] = ''
                    st.session_state[f'customer_search_desc_value'] = ''
                    st.session_state[f'customer_search_phone_value'] = ''
                    st.session_state['reset_triggered_for_customer_search'] = True
                else:
                    if not st.session_state.get('reset_triggered_for_customer_search', False):
                        st.session_state[f'customer_search_name_value'] = self.name
                        st.session_state[f'customer_search_desc_value'] = self.desc
                        st.session_state[f'customer_search_phone_value'] = self.phone
                st.session_state['reset_triggered_for_customer_search'] = False


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
            if f'search_entrega_cliente_value' not in st.session_state: st.session_state.search_entrega_cliente_value = None
            if f'search_customer_value' not in st.session_state: st.session_state.search_customer_value = ""
            if f'search_item_value' not in st.session_state: st.session_state.search_item_value = ""
            if f'search_proveedor_value' not in st.session_state: st.session_state.search_proveedor_value = "" 
            if f'search_pagado_value' not in st.session_state: st.session_state.search_pagado_value = "" 
            if f'search_limite_value' not in st.session_state: st.session_state.search_limite_value = None
            if f'search_entrega_proveedor_value' not in st.session_state: st.session_state.search_entrega_proveedor_value = None
            if f'search_recogida_proveedor_value' not in st.session_state: st.session_state.search_recogida_proveedor_value = None
            if f'search_recogida_cliente_value' not in st.session_state: st.session_state.search_recogida_cliente_value = None
            
            if 'reset_triggered_for_order_search' not in st.session_state:
                st.session_state['reset_triggered_for_order_search'] = False

        elif formType == 'submit':
            if 'submit_entrega_cliente_input_key' not in st.session_state or st.session_state.get('reset_triggered_for_order_submit', False):
                st.session_state.submit_entrega_cliente_input_key = datetime.date.today()

            if 'submit_customer_selectbox_key_input' not in st.session_state or st.session_state.get('reset_triggered_for_order_submit', False): 
                st.session_state.submit_customer_selectbox_key_input = "" 
            if 'submit_item_selectbox_key_input' not in st.session_state or st.session_state.get('reset_triggered_for_order_submit', False): 
                st.session_state.submit_item_selectbox_key_input = "" 
            if 'submit_descripcion_input_key' not in st.session_state or st.session_state.get('reset_triggered_for_order_submit', False): 
                st.session_state.submit_descripcion_input_key = "" 
            if 'submit_cantidad_input_key' not in st.session_state or st.session_state.get('reset_triggered_for_order_submit', False): 
                st.session_state.submit_cantidad_input_key = 1.0
            if 'submit_proveedor_selectbox_key' not in st.session_state or st.session_state.get('reset_triggered_for_order_submit', False):
                st.session_state.submit_proveedor_selectbox_key = "" 
            if 'submit_pagado_selectbox_key' not in st.session_state or st.session_state.get('reset_triggered_for_order_submit', False):
                st.session_state.submit_pagado_selectbox_key = "No Pagado" 
            if 'submit_limite_input_key' not in st.session_state or st.session_state.get('reset_triggered_for_order_submit', False): # No default to today for 'Limite'
                st.session_state.submit_limite_input_key = None 


        # Main form logic
        # Set clear_on_submit to False and handle clearing manually with a reset button
        # This prevents the form from clearing on *every* rerun or when validation fails
        with st.form(key=f'order-form-{formType}', clear_on_submit=((formType == 'submit' or formType == 'search') and st.session_state.get('reset_triggered_for_order_submit', False))): # Adjusted clear_on_submit logic
            st.write(title)
            
            if formType == 'submit':
                proveedor_options = ["", "Alicia", "Dani", "Manuela", "Mari", "Marlen", "Marta"]
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
                        key='submit_customer_autocomplete_key' 
                    )
                    self.item = st.selectbox(
                        'Articulo', 
                        list_items, 
                        key='submit_item_autocomplete_key' 
                    )
                    
                    self.desc = st.text_input(
                        'Descripcion', 
                        value=st.session_state.submit_descripcion_input_key, 
                        key='submit_descripcion_input_key'
                    )

                with col2submit:
                    self.quantity = st.number_input(
                        'Cantidad', 
                        min_value=1.0,
                        max_value=None, 
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
                        value=st.session_state.submit_limite_input_key, 
                        format="DD/MM/YYYY", 
                        key='submit_limite_input_key'
                    )
                
                # Buttons for submission form
                col_buttons = st.columns(2)
                with col_buttons[0]:
                    self.Button = st.form_submit_button(buttonName) 
                with col_buttons[1]:
                    self.ButtonReset = st.form_submit_button('Borrar formulario')
                    if self.ButtonReset:
                        # Clear specific session state keys for the submit form
                        # Estas asignaciones SÍ son necesarias para resetear los valores por defecto
                        st.session_state.submit_entrega_cliente_input_key = datetime.date.today()
                        st.session_state.submit_customer_selectbox_key_input = "" 
                        st.session_state.submit_item_selectbox_key_input = "" 
                        st.session_state.submit_descripcion_input_key = "" 
                        st.session_state.submit_cantidad_input_key = 1.0
                        st.session_state.submit_proveedor_selectbox_key = "" 
                        st.session_state.submit_pagado_selectbox_key = "No Pagado" 
                        st.session_state.submit_limite_input_key = None
                        st.session_state['reset_triggered_for_order_submit'] = True # Set a flag

                # Important: Update session state after form submit (if not a reset)
                # SOLO ASIGNAR LOS VALORES QUE NO ESTÁN VINCULADOS DIRECTAMENTE A session_state MEDIANTE SU CLAVE
                if self.Button and not st.session_state.get('reset_triggered_for_order_submit', False):

                    pass 
                
                # Reset the flag AFTER processing for next run
                # La bandera debe resetearse para la próxima ejecución del script
                st.session_state['reset_triggered_for_order_submit'] = False

            else:
                proveedor_options = ["", "Alicia", "Dani", "Manuela", "Mari", "Marlen", "Marta"]
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
                    self.customer = st.text_input(
                        'Cliente', 
                        value=st.session_state.search_customer_value, 
                        key='search_customer_key'
                    )
                    self.item = st.text_input(
                        'Articulo', 
                        value=st.session_state.search_item_value, 
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
                    st.session_state.search_entrega_cliente_value = None
                    st.session_state.search_customer_value = ""
                    st.session_state.search_item_value = ""
                    st.session_state.search_proveedor_value = ""
                    st.session_state.search_pagado_value = ""
                    st.session_state.search_limite_value = None
                    st.session_state.search_entrega_proveedor_value = None
                    st.session_state.search_recogida_proveedor_value = None
                    st.session_state.search_recogida_cliente_value = None
                
                else: # Only update if submit button was pressed and not reset

                    if not st.session_state.get('reset_triggered_for_order_search', False):
                        st.session_state.search_entrega_cliente_value = self.deliveryDate
                        st.session_state.search_customer_value = self.customer
                        st.session_state.search_item_value = self.item
                        st.session_state.search_proveedor_value = self.supplier
                        st.session_state.search_pagado_value = self.paid
                        st.session_state.search_limite_value = self.limit
                        st.session_state.search_entrega_proveedor_value = self.entrega_proveedor
                        st.session_state.search_recogida_proveedor_value = self.recogida_proveedor
                        st.session_state.search_recogida_cliente_value = self.recogida_cliente

                st.session_state['reset_triggered_for_order_search'] = False