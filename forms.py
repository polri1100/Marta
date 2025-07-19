import streamlit as st
import functions as f
import pandas as pd
import datetime

class ItemForm():
    def __init__(self, formType, title, buttonName):
        list_items = []
        if formType == 'search':
            try:
                db_articulos = f.obtainTable('Articulos')
                if not db_articulos.empty and 'Articulo' in db_articulos.columns:
                    list_items = db_articulos['Articulo'].unique().tolist()
            except Exception as e:
                st.warning(f"No se pudieron cargar artículos para sugerencias: {e}")

        with st.form(key=f'item-form-{formType}', clear_on_submit=(formType == 'submit')):
            st.write(title)

            if formType == 'search':
                self.item = f.autocomplete_text_input('Articulo', '', list_items, key=f'item_search_articulo_{formType}')
                self.desc = st.text_input('Descripción', key=f'item_search_descripcion_{formType}', value=st.session_state.get(f'item_search_descripcion_value', ''))


                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')

        # --- CAMBIO CLAVE AQUÍ: Almacenar los valores en session_state tras cada interacción ---
        if formType == 'search':
            # Solo actualizamos session_state si no es el botón de reset el que se presionó en este ciclo
            # para no sobrescribir el valor vacío que pusimos para el reset.
            if not (self.ButtonReset and st.session_state.get('reset_triggered_for_search', False)):
                st.session_state[f'item_search_articulo_value'] = self.item
                st.session_state[f'item_search_descripcion_value'] = self.desc
            
            # Resetear la bandera de reinicio
            if self.ButtonReset:
                st.session_state['reset_triggered_for_search'] = True
            else:
                st.session_state['reset_triggered_for_search'] = False

        
class CustomerForm():
    def __init__(self, formType, title, buttonName):
        # Esta lista de clientes puede no ser necesaria si solo haces text_input
        # Pero la dejo si la tenías por algún st.selectbox o similar
        list_customers = []
        if formType == 'search':
            try:
                db_clientes = f.obtainTable('Clientes')
                if not db_clientes.empty and 'Nombre' in db_clientes.columns:
                    list_customers = db_clientes['Nombre'].unique().tolist()
            except Exception as e:
                st.warning(f"No se pudieron cargar clientes para sugerencias: {e}")

        with st.form(key=f'customer-form-{formType}', clear_on_submit=(formType == 'submit')):
            st.write(title)

            if formType == 'submit':
                # Campos para el formulario de INSERCIÓN (mantén tus campos originales aquí)
                self.name = st.text_input('Nombre', key=f'customer_submit_name_{formType}')
                self.desc = st.text_input('Descripción', key=f'customer_submit_desc_{formType}')
                self.phone = st.text_input('Teléfono', key=f'customer_submit_phone_{formType}')
                
                self.Button = st.form_submit_button(buttonName)
                self.ButtonReset = None

            else: # formType == 'search'
                # Campos para el formulario de BÚSQUEDA (solo los que quieres para buscar)
                # Usar las claves de session_state directamente en 'value'
                self.name = st.text_input('Nombre', key=f'customer_search_name_{formType}', 
                                        value=st.session_state.get(f'customer_search_name_value', ''))
                self.desc = st.text_input('Descripción', key=f'customer_search_desc_{formType}',
                                        value=st.session_state.get(f'customer_search_desc_value', ''))
                self.phone = st.text_input('Teléfono', key=f'customer_search_phone_{formType}',
                                        value=st.session_state.get(f'customer_search_phone_value', ''))


                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName)
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')

        # --- CAMBIO CLAVE AQUÍ: Almacenar los valores en session_state tras cada interacción ---
        # Esto asegura que los valores de los inputs estén disponibles fuera del formulario
        if formType == 'search':
            # Solo actualizamos session_state si no es el botón de reset el que se presionó en este ciclo
            if not (self.ButtonReset and st.session_state.get('reset_triggered_for_customer_search', False)):
                st.session_state[f'customer_search_name_value'] = self.name
                st.session_state[f'customer_search_desc_value'] = self.desc
                st.session_state[f'customer_search_phone_value'] = self.phone

            
            # Resetear la bandera de reinicio
            if self.ButtonReset:
                st.session_state['reset_triggered_for_customer_search'] = True
            else:
                st.session_state['reset_triggered_for_customer_search'] = False

class OrderForm():
    def __init__(self, formType, title, buttonName, list_items=None, list_customers=None, db_articulos=None):
        if list_items is None: list_items = []
        if list_customers is None: list_customers = []
        
        # --- Estricta Inicialización de Variables de Session State para el Formulario de Inserción (Submit) ---
        # (Esto está bien, se usa para el formulario de submit. No lo tocaremos por ahora, ya que funciona.)
        if 'entrega_cliente_input_key' not in st.session_state: 
            st.session_state.entrega_cliente_input_key = datetime.date.today()
        if 'customer_selectbox_key' not in st.session_state: 
            st.session_state.customer_selectbox_key = "" 
        if 'item_selectbox_key' not in st.session_state: 
            st.session_state.item_selectbox_key = "" 
        if 'descripcion_input_key' not in st.session_state: 
            st.session_state.descripcion_input_key = "" 
        if 'cantidad_input_key' not in st.session_state: 
            st.session_state.cantidad_input_key = 1.0
        if 'proveedor_selectbox_key' not in st.session_state:
            st.session_state.proveedor_selectbox_key = "" 
        if 'pagado_selectbox_key' not in st.session_state:
            st.session_state.pagado_selectbox_key = "No Pagado" 
        if 'limite_input_key' not in st.session_state: 
            st.session_state.limite_input_key = None 
            
        # --- Inicialización de Variables de Session State para el Formulario de Búsqueda (Search) ---
        # Asegurarse de que las claves de sesión para búsqueda existen y tienen un valor por defecto.
        # Esto es CRUCIAL para que Streamlit sepa qué valores usar y cómo limpiarlos.
        if 'order_search_delivery_date_value' not in st.session_state: st.session_state.order_search_delivery_date_value = None
        if 'order_search_customer_value' not in st.session_state: st.session_state.order_search_customer_value = ""
        if 'order_search_item_value' not in st.session_state: st.session_state.order_search_item_value = ""
        if 'order_search_supplier_value' not in st.session_state: st.session_state.order_search_supplier_value = ""
        if 'order_search_paid_value' not in st.session_state: st.session_state.order_search_paid_value = "" # Puede ser 'No Pagado', 'Efectivo', etc.
        if 'order_search_limit_value' not in st.session_state: st.session_state.order_search_limit_value = None
        # Si tienes más campos de búsqueda como Entrega_Proveedor, Recogida_Proveedor, Recogida_Cliente, añádelos aquí:
        if 'order_search_entrega_proveedor_value' not in st.session_state: st.session_state.order_search_entrega_proveedor_value = None
        if 'order_search_recogida_proveedor_value' not in st.session_state: st.session_state.order_search_recogida_proveedor_value = None
        if 'order_search_recogida_cliente_value' not in st.session_state: st.session_state.order_search_recogida_cliente_value = None
        
        
        # Lógica principal del formulario
        if formType == 'submit':
            proveedor_options = ["", "Alicia", "Dani", "Manuela", "Mari", "Marlen", "Marta"]
            pagado_options = ["No Pagado", "Efectivo", "Tarjeta", "Bizum"] 

            with st.form(key=f'order-form-{formType}', clear_on_submit=(formType == 'submit')):
                st.write(title)
                col1submit, col2submit = st.columns(2)

                with col1submit:
                    self.entregaCliente = st.date_input(
                        'Entrega_Cliente', 
                        format="DD/MM/YYYY", 
                        key='entrega_cliente_input_key'
                    )

                    self.customer = f.autocomplete_text_input(
                        'Cliente', 
                        st.session_state.customer_selectbox_key, 
                        list_customers, 
                        'customer_selectbox_key'
                    )
                    self.item = f.autocomplete_text_input(
                        'Articulo', 
                        st.session_state.item_selectbox_key, 
                        list_items, 
                        'item_selectbox_key'
                    )
                    
                    self.desc = st.text_input(
                        'Descripcion', 
                        value=st.session_state.descripcion_input_key, 
                        key='descripcion_input_key'
                    )


                with col2submit:
                    self.quantity = st.number_input(
                        'Cantidad', 
                        min_value=1.0,
                        max_value=None, 
                        step=1.0, 
                        key='cantidad_input_key'
                    )

                    self.supplier = st.selectbox(
                        'Proveedor', 
                        proveedor_options, 
                        index=(proveedor_options.index(st.session_state.proveedor_selectbox_key) if st.session_state.proveedor_selectbox_key in proveedor_options else 0),
                        key='proveedor_selectbox_key'
                    )
                    
                    self.paid = st.selectbox(
                        'Pagado', 
                        pagado_options, 
                        index=(pagado_options.index(st.session_state.pagado_selectbox_key) if st.session_state.pagado_selectbox_key in pagado_options else 0),
                        key='pagado_selectbox_key'
                    )

                    self.limit = st.date_input(
                        'Limite', 
                        value=st.session_state.limite_input_key, 
                        format="DD/MM/YYYY", 
                        key='limite_input_key'
                    )



                # Botón de envío dentro del formulario 'submit'
                self.Button = st.form_submit_button(buttonName) 

        else: # formType == 'search'
            # Inicializar los valores de los inputs de búsqueda desde session_state
            # Esto es lo que permite que los campos retengan su valor y que el botón de borrar funcione
            # Asegúrate de que los `key`s de los inputs sean los mismos que los usados para inicializar session_state arriba.
            # Y que los `value` de los inputs apunten a esas claves de session_state.
            with st.form(key=f'order-form-{formType}'):
                st.write(title) 
                
                # Campos de búsqueda, apuntando a session_state para su valor
                self.deliveryDate = st.date_input('Entrega_Cliente', value=st.session_state.order_search_delivery_date_value, format="DD/MM/YYYY", key='order_search_delivery_date_key')
                self.customer = st.text_input('Cliente', value=st.session_state.order_search_customer_value, key='order_search_customer_key')
                self.item = st.text_input('Articulo', value=st.session_state.order_search_item_value, key='order_search_item_key')

                self.supplier = st.text_input('Proveedor', value=st.session_state.order_search_supplier_value, key='order_search_supplier_key')
                self.paid = st.text_input('Pagado', value=st.session_state.order_search_paid_value, key='order_search_paid_key')
                self.limit = st.date_input('Limite', value=st.session_state.order_search_limit_value, format="DD/MM/YYYY", key='order_search_limit_key')
                
                # Añade aquí los otros campos de fecha de búsqueda si los necesitas
                self.entrega_proveedor = st.date_input('Entrega Proveedor', value=st.session_state.order_search_entrega_proveedor_value, format="DD/MM/YYYY", key='order_search_entrega_proveedor_key')
                self.recogida_proveedor = st.date_input('Recogida Proveedor', value=st.session_state.order_search_recogida_proveedor_value, format="DD/MM/YYYY", key='order_search_recogida_proveedor_key')
                self.recogida_cliente = st.date_input('Recogida Cliente', value=st.session_state.order_search_recogida_cliente_value, format="DD/MM/YYYY", key='order_search_recogida_cliente_key')


                col1search, col2search = st.columns(2)
                with col1search:
                    self.Button = st.form_submit_button(buttonName) 
                with col2search:
                    self.ButtonReset = st.form_submit_button('Borrar búsqueda')

            # --- Guardar los valores de los inputs de búsqueda en session_state tras cada interacción ---
        if formType == 'search':
            # Solo actualizamos session_state si no es el botón de reset el que se presionó en este ciclo
            if not (self.ButtonReset and st.session_state.get('reset_triggered_for_customer_search', False)):
                st.session_state[f'order_search_delivery_date_value'] = self.deliveryDate
                st.session_state[f'order_search_customer_value'] = self.customer
                st.session_state[f'order_search_item_value'] = self.item
                st.session_state[f'order_search_supplier_value'] = self.supplier
                st.session_state[f'order_search_paid_value'] = self.paid
                st.session_state[f'order_search_limit_value'] = self.limit
                st.session_state[f'order_search_entrega_proveedor_value'] = self.entrega_proveedor
                st.session_state[f'order_search_recogida_proveedor_value'] = self.recogida_proveedor
                st.session_state[f'order_search_recogida_cliente_value'] = self.recogida_cliente
            
            # Resetear la bandera de reinicio
            if self.ButtonReset:
                st.session_state['reset_triggered_for_customer_search'] = True
            else:
                st.session_state['reset_triggered_for_customer_search'] = False

