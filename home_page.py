import streamlit as st
import functions as f
import pandas as pd

def home_content():
    st.markdown("# EL TALLER DE MARTA 👚")
    st.write(f"¡Bienvenida, {st.user.name} a la aplicación de gestión de tu negocio!")

    st.markdown("---") 
    st.markdown("# Seguimiento de Pedidos 🗓️")

    # --- Funciones para cargar y filtrar datos de la base de datos ---
    # Usamos st.cache_data para obtener la tabla completa.


    # --- Cargamos todos los datos necesarios ---
    pedidos = f.get_orders_data()
    clientes = f.get_clients_data()
    articulos = f.get_articles_data()

    # Solo procesamos si tenemos datos
    if not pedidos.empty:
        # Unir datos para tener el nombre del cliente y el artículo
        pedidos_join = f.ordersJoin(pedidos, clientes, articulos)
        
        # Asegurarse de que las columnas de fecha sean tipo datetime
        for col in ['Entrega_Cliente', 'Entrega_Proveedor', 'Recogida_Proveedor', 'Recogida_Cliente']:
            pedidos_join[col] = pd.to_datetime(pedidos_join[col], errors='coerce')
        
        # --- FILTRADO DE PEDIDOS ---
        # Pedidos actuales: sin fecha de recogida_cliente
        pedidos_actuales = pedidos_join[pedidos_join['Recogida_Cliente'].isnull()].copy()

        # Si la tabla de pedidos_actuales está vacía, no hay nada que mostrar
        if pedidos_actuales.empty:
            st.info("No hay pedidos pendientes de entrega al cliente. ¡Todos los pedidos están completados!")
        else:
            # Categorías de los pedidos
            local_para_costurera = pedidos_actuales[pedidos_actuales['Entrega_Proveedor'].isnull()]
            costurera = pedidos_actuales[pedidos_actuales['Entrega_Proveedor'].notnull() & pedidos_actuales['Recogida_Proveedor'].isnull()]
            local_para_entregar = pedidos_actuales[pedidos_actuales['Recogida_Proveedor'].notnull() & pedidos_actuales['Entrega_Cliente'].notnull()]
            
            # --- DISEÑO DE LA INTERFAZ CON 3 COLUMNAS ---
            col1, col2, col3 = st.columns(3)

            # Contenedor 1: Local para costurera
            with col1:
                st.markdown("### Local para costurera")
                st.info(f"Pedidos: {len(local_para_costurera)}")
                
                # Mostrar tarjetas de los pedidos
                for index, row in local_para_costurera.iterrows():
                    with st.expander(f"{row['Cliente']} | {row['Articulo']}"):
                        st.write(f"**Fecha de Entrega:** {row['Entrega_Cliente'].strftime('%d/%m/%Y') if pd.notna(row['Entrega_Cliente']) else 'No asignada'}")
                        st.write(f"**Cliente:** {row['Cliente']}")
                        st.write(f"**Descripción:** {row['Descripcion']}")

            # Contenedor 2: En la costurera
            with col2:
                st.markdown("### En la costurera")
                st.info(f"Pedidos: {len(costurera)}")
                
                # Mostrar tarjetas de los pedidos
                for index, row in costurera.iterrows():
                    with st.expander(f"{row['Cliente']} | {row['Articulo']}"):
                        st.write(f"**Fecha de Entrega:** {row['Entrega_Cliente'].strftime('%d/%m/%Y') if pd.notna(row['Entrega_Cliente']) else 'No asignada'}")
                        st.write(f"**Cliente:** {row['Cliente']}")
                        st.write(f"**Descripción:** {row['Descripcion']}")
                        st.write(f"**Costurera:** {row['Proveedor']}")

            # Contenedor 3: Local para entregar
            with col3:
                st.markdown("### Local para entregar")
                st.info(f"Pedidos: {len(local_para_entregar)}")

                # Mostrar tarjetas de los pedidos
                for index, row in local_para_entregar.iterrows():
                    with st.expander(f"{row['Cliente']} | {row['Articulo']}"):
                        st.write(f"**Fecha de Entrega:** {row['Entrega_Cliente'].strftime('%d/%m/%Y') if pd.notna(row['Entrega_Cliente']) else 'No asignada'}")
                        st.write(f"**Cliente:** {row['Cliente']}")
                        st.write(f"**Descripción:** {row['Descripcion']}")



    else:
        st.warning("No hay pedidos en la base de datos para mostrar.")

