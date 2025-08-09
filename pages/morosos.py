import streamlit as st
import functions as f
import pandas as pd


st.markdown("# Morosos")
st.markdown("---")

pedidos_df = f.obtainTable('Pedidos')

if not pedidos_df.empty:
        # Unimos las tablas para tener la información completa
        db_clientes = f.obtainTable('Clientes')
        db_articulos = f.obtainTable('Articulos')
        pedidos_join = f.ordersJoin(pedidos_df, db_clientes, db_articulos)
        
        # Filtramos los pedidos que han sido entregados pero no pagados
        pedidos_morosos = pedidos_join[
            (pedidos_join['Recogida_Cliente'].notna()) & 
            (pedidos_join['Pagado'] == 'No Pagado')
        ].copy()

        # Si hay pedidos morosos, los mostramos
        if not pedidos_morosos.empty:
            st.subheader("Lista de pedidos entregados y no pagados")
            st.warning("⚠️ ALERTA MOROSOS", icon="🚨")
            
            # Limpiamos las columnas de IDs que no necesitamos
            if 'Cliente_id' in pedidos_morosos.columns:
                pedidos_morosos = pedidos_morosos.drop(columns=['Cliente_id'])
            if 'Articulo_id' in pedidos_morosos.columns:
                pedidos_morosos = pedidos_morosos.drop(columns=['Articulo_id'])

            st.dataframe(pedidos_morosos)
        else:
            # Mensaje cuando no hay morosos
            st.success("¡No hay pedidos morosos! Todos los pedidos entregados han sido pagados. 🎉")
else:
        st.info("La tabla de pedidos está vacía. No hay datos para verificar.")
