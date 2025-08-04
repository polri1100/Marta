import streamlit as st
import functions as f
import forms
import pandas as pd
import time
import datetime



st.markdown("# Insertar Pedidos ➕")

# Load databases for display (without normalized columns)
db_pedidos = f.obtainTable('Pedidos')
db_articulos_display = f.obtainTable('Articulos') # For display and list_items
db_clientes_display = f.obtainTable('Clientes')   # For display and list_customers

# Load databases for internal lookups (with normalized columns)
db_articulos_lookup = f.obtainTableWithNormalized('Articulos')
db_clientes_lookup = f.obtainTableWithNormalized('Clientes')

# Join Databases for display
db_joined = f.ordersJoin(db_pedidos, db_clientes_display, db_articulos_display)

# Remove ID columns from join result if they are still present after the join logic
# These are internal IDs from the join, not the main Pedido ID
if 'Cliente_id' in db_joined.columns:
    db_joined = db_joined.drop(columns=['Cliente_id'])
if 'Articulo_id' in db_joined.columns:
    db_joined = db_joined.drop(columns=['Articulo_id'])


# Table calculations
list_items = db_articulos_display['Articulo'].unique().tolist() if not db_articulos_display.empty and 'Articulo' in db_articulos_display.columns else []
list_items.sort()
placeholder_items = ['-Selecciona Un Artículo-']+list_items
list_customers = db_clientes_display['Nombre'].unique().tolist() if not db_clientes_display.empty and 'Nombre' in db_clientes_display.columns else []
list_customers.sort()
placeholder_customers = ['-Selecciona Un Cliente-']+ list_customers
max_id, min_id = f.returnMaxMinID(db_pedidos)

# --- Insertion Form ---
st.subheader('Nuevo Pedido')
formSubmit = forms.OrderForm('submit', 'Formulario para Insertar Nuevo Pedido', 'Guardar registro', placeholder_items, placeholder_customers)

# --- Handle the submit action *outside* the form definition ---
if formSubmit.Button:
    # Validaciones antes de insertar:
    # AHORA USAMOS DIRECTAMENTE LOS ATRIBUTOS DE LA INSTANCIA formSubmit
    # QUE CONTIENEN LOS VALORES ENVIADOS EN ESTA EJECUCIÓN
    if formSubmit.customer == '-Selecciona Un CLiente-':
        st.warning("Por favor, introduce un nombre de cliente.",icon="⚠️")
        # No uses st.stop() aquí si quieres que el usuario vea el formulario con los errores
        # y pueda corregir sin perder lo que ya escribió.
        st.stop()
    if formSubmit.item == '-Selecciona Un Articulo-':
        st.warning("Por favor, introduce un nombre de artículo.",icon="⚠️")
        st.stop()
    if not formSubmit.customer or not formSubmit.item:
        st.warning("Por favor, corrige los errores en el formulario para poder insertar el pedido.",icon="⚠️")
        # Salir de este bloque if para que el formulario se muestre con los errores
        # y el usuario pueda corregir y volver a intentar.
    else: # Solo procede si ambas validaciones iniciales pasan
        cliente_id = None
        # Usar formSubmit.customer directamente para la normalización
        entered_customer_normalized = f.normalize_string(formSubmit.customer) 

        if not db_clientes_lookup.empty:
            filtered_cliente = db_clientes_lookup[db_clientes_lookup['Nombre_Normalized'] == entered_customer_normalized]
            if not filtered_cliente.empty:
                cliente_id = int(filtered_cliente['ID'].iloc[0])
            else:
                st.warning(f"Por favor, selecciona un cliente válido de las sugerencias o créalo primero.",icon="⚠️")
                st.stop() # No parar si queremos que el usuario pueda corregir
        else:
            st.error("No se pudo cargar la lista de clientes para validación.")
            st.stop()

        articulo_id = None
        articulo_coste_material = 0.0
        articulo_coste_proveedor = 0.0
        articulo_importe = 0.0
        if formSubmit.quantity == 0.0:
            formSubmit.quantity = 1.0
        cantidad = float(formSubmit.quantity)

        # Usar formSubmit.item directamente para la normalización
        entered_item_normalized = f.normalize_string(formSubmit.item)
        
        if not db_articulos_lookup.empty:
            filtered_articulo = db_articulos_lookup[db_articulos_lookup['Articulo_Normalized'] == entered_item_normalized]
            if not filtered_articulo.empty:
                articulo_id = int(filtered_articulo['ID'].iloc[0])
                if 'Coste_Material_Sugerido' in filtered_articulo.columns:
                    articulo_coste_material = float(filtered_articulo['Coste_Material_Sugerido'].iloc[0])*cantidad
                if 'Coste_Proveedor_Sugerido' in filtered_articulo.columns:
                    articulo_coste_proveedor = float(filtered_articulo['Coste_Proveedor_Sugerido'].iloc[0])*cantidad
                if 'Importe_Sugerido' in filtered_articulo.columns:
                    articulo_importe = float(filtered_articulo['Importe_Sugerido'].iloc[0])*cantidad
            else:
                st.warning(f"Artículo '{formSubmit.item}' no encontrado en la base de datos de artículos. Los costes se establecerán en 0.",icon="⚠️")
                # Do not stop here, allow insertion with default costs if article not found, but warn user
        else:
            st.error("No se pudo cargar la lista de artículos para validación. No se puede insertar el pedido.")
            st.stop()
            # Salir del callback del botón

        # Solo si ambos IDs son válidos, procedemos con la inserción
        if cliente_id is not None and articulo_id is not None:
            new_order_data = {
                'Entrega_Cliente': formSubmit.entregaCliente, # Usar el atributo del form
                'Cliente_id': cliente_id,
                'Articulo_id': articulo_id,
                'Descripcion': formSubmit.desc, # Usar el atributo del form
                'Cantidad': formSubmit.quantity, # Usar el atributo del form
                'Proveedor': formSubmit.supplier if formSubmit.supplier else None, # Usar el atributo del form
                'Pagado': formSubmit.paid, # Usar el atributo del form
                'Limite': formSubmit.limit, # Usar el atributo del form
                'Coste_Material': articulo_coste_material,
                'Coste_Proveedor': articulo_coste_proveedor,
                'Importe': articulo_importe,
                'Entrega_Proveedor': None, # Ensure these are explicitly None if not set
                'Recogida_Proveedor': None,
                'Recogida_Cliente': None,
            }
            
            # Convert date objects to ISO format strings for database insertion
            for key, value in new_order_data.items():
                if isinstance(value, datetime.date):
                    new_order_data[key] = value.isoformat()
            
            # Filter out empty strings/None if your DB strict about them.
            final_payload = {k: v for k, v in new_order_data.items() if v is not None and v != ''}


            response = f.insert_record('Pedidos', final_payload)
            if response:
                st.success("Pedido insertado con éxito!", icon="✅")
                # Disparar el reseteo del formulario en la próxima ejecución
                for k in ['submit_proveedor_selectbox_key', 'submit_pagado_selectbox_key','submit_cantidad_input_key','submit_limite_input_key']:
                    if k in st.session_state:
                        del st.session_state[k]
                
                st.rerun() # Rerun to show cleared form and updated table
            else:
                st.error("No se pudo insertar el pedido debido a un problema con la base de datos.")
        else:
            # Este else captura si alguna de las validaciones de ID falló y se usó 'return'
            st.warning("La inserción fue cancelada debido a validaciones fallidas. Por favor, revisa los mensajes de error/advertencia.",icon="⚠️")
            st.stop()

                        
st.markdown("---")

## Pedidos con Entrega Hoy

today = datetime.date.today()
if not db_joined.empty:
    db_joined['Entrega_Cliente_Date'] = pd.to_datetime(db_joined['Entrega_Cliente'], errors='coerce').dt.date
    today_orders = db_joined[db_joined['Entrega_Cliente_Date'] == today].drop(columns=['Entrega_Cliente_Date']).copy()
else:
    today_orders = pd.DataFrame() 

if not today_orders.empty:
    # Ensure correct columns are present for display and editing, especially 'Pagado' and 'Proveedor'
    # And 'ID' should be the Pedido ID, not Cliente_id or Articulo_id
    column_config_today = {
        "ID": st.column_config.NumberColumn("ID del Pedido", disabled=True),
        "Cliente": st.column_config.TextColumn("Cliente", disabled=True),
        "Articulo": st.column_config.TextColumn("Artículo", disabled=True),
        "Entrega_Cliente": st.column_config.DateColumn("Entrega Cliente", format="DD/MM/YYYY"),
        "Limite": st.column_config.DateColumn("Límite", format="DD/MM/YYYY"),
        "Entrega_Proveedor": st.column_config.DateColumn("Entrega Proveedor", format="DD/MM/YYYY"),
        "Recogida_Proveedor": st.column_config.DateColumn("Recogida Proveedor", format="DD/MM/YYYY"),
        "Recogida_Cliente": st.column_config.DateColumn("Recogida Cliente", format="DD/MM/YYYY"),
        "Pagado": st.column_config.SelectboxColumn(
            "Pagado",
            options=["No Pagado", "Efectivo", "Tarjeta", "Bizum"],
            required=True,
        ),
        "Proveedor": st.column_config.SelectboxColumn(
            "Proveedor",
            options=["", "Alicia", "Dani", "Manuela", "Mari", "Marlen","M.Antonia", "Marta"],
            required=False,
        ),
        "Coste_Material": st.column_config.NumberColumn("Coste Material", format="%.2f", step=0.01),
        "Coste_Proveedor": st.column_config.NumberColumn("Coste Proveedor", format="%.2f", step=0.01),
        "Importe": st.column_config.NumberColumn("Importe", format="%.2f", step=0.01),
        "Descripcion": st.column_config.TextColumn("Descripcion"),
        "Cantidad": st.column_config.NumberColumn("Cantidad", min_value=1.0, step=1.0),
    }

    st.dataframe(today_orders, key='today_orders_data_editor', column_config=column_config_today, hide_index=True)
else:
    st.info("No hay pedidos para mostrar de hoy")

