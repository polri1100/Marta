import streamlit as st
import functions as f
import pandas as pd
import datetime


st.markdown("# Proveedores")
st.markdown("---")

costureras = ["Alicia", "Dani", "Manuela", "Mari", "Marlen", "M.Antonia", "Marta"]

pedidos_df = f.get_orders_data()

if not pedidos_df.empty:

    db_clientes = f.get_clients_data()
    db_articulos = f.get_articles_data()
    pedidos_join = f.ordersJoin(pedidos_df, db_clientes, db_articulos)

    pedidos_join["Recogida_Proveedor"] = pd.to_datetime(pedidos_join["Recogida_Proveedor"], errors = "coerce")
    pedidos_join["Pago_Proveedor"] = pd.to_datetime(pedidos_join["Pago_Proveedor"], errors = "coerce")
    
    pendientes_de_pago = pedidos_join[
                        (pedidos_join["Recogida_Proveedor"].notna()) &
                        (pedidos_join["Proveedor"].notna()) &
                        (pedidos_join["Pago_Proveedor"].isna()) 
                        ].copy()

    if not pendientes_de_pago.empty:

        costureras_disponibles = sorted(list(pendientes_de_pago["Proveedor"].unique()))
        costurera_seleccionada = st.selectbox(
            "Filtrar por Costurera:",
            options = ["Mostrar Todos"] + costureras_disponibles
        )

        if costurera_seleccionada != "Mostrar Todos":
            pendientes_de_pago = pendientes_de_pago[pendientes_de_pago["Proveedor"] == costurera_seleccionada]
        
        if pendientes_de_pago.empty:
            st.info("No hay pedidos por pagar de esta costurera")
        
        pendientes_de_pago["Seleccionar"] = False

        st.subheader(f"Hay {len(pendientes_de_pago)} pedidos pendientes por pagar")

        st.session_state["df_pagos"] = st.data_editor(
            pendientes_de_pago[["ID","Cliente", "Articulo", "Descripcion","Seleccionar", "Proveedor", "Recogida_Proveedor" ]],
            column_order = ["Seleccionar", "Cliente", "Articulo", "Descripcion"] 
        )

        col1, col2, col3 = st.columns([1,1,1])
        with col1:
            if st.button("Pagar"):
                selected_rows = st.session_state["df_pagos"][st.session_state["df_pagos"]["Seleccionar"]]
                if selected_rows.empty:
                    st.warning("No se ha seleccionado ningún pedido")
                else:
                    pedidos_pagar = selected_rows["ID"].tolist()

                    hoy = datetime.date.today().isoformat()

                    update_payload = {"Pago_Proveedor" : hoy}

                    if update_payload:
                        for pedidos_id in pedidos_pagar:
                            f.update_record("Pedidos", pedidos_id, update_payload)
                    st.cache_data.clear()
                    if 'df_display_orders' in st.session_state:
                        del st.session_state['df_display_orders']
                    st.rerun()

    else:
        st.success("Todos los Pedidos están pagados :D")


else:
    st.warning("No hay datos en pedidos")


