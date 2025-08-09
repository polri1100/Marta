import streamlit as st
import functions as f
import pandas as pd
import datetime


st.markdown("# Pedidos Abandonados")
st.markdown("---")

pedidos_df = f.obtainTable('Pedidos')

if not pedidos_df.empty:
        # Unimos las tablas para tener la información completa
        db_clientes = f.obtainTable('Clientes')
        db_articulos = f.obtainTable('Articulos')
        pedidos_join = f.ordersJoin(pedidos_df, db_clientes, db_articulos)
        
        # Obtenemos la fecha de hoy
        hoy = pd.to_datetime(datetime.date.today())

        # Convertir las columnas de fecha a datetime de pandas
        pedidos_join['Recogida_Proveedor'] = pd.to_datetime(pedidos_join['Recogida_Proveedor'], errors='coerce')
        pedidos_join['Recogida_Cliente'] = pd.to_datetime(pedidos_join['Recogida_Cliente'], errors='coerce')

        # Filtramos los pedidos que cumplen las condiciones de abandono
        pedidos_abandonados = pedidos_join[
            # Tiene fecha de Recogida_Proveedor y no es NaT
            (pedidos_join['Recogida_Proveedor'].notna()) & 
            # NO tiene fecha de Recogida_Cliente
            (pedidos_join['Recogida_Cliente'].isna())
        ].copy()
        
        if not pedidos_abandonados.empty:
            # Calcular la diferencia de días y filtrar
            pedidos_abandonados['Dias_Desde_Recogida'] = (hoy - pedidos_abandonados['Recogida_Proveedor']).dt.days
            pedidos_abandonados = pedidos_abandonados[pedidos_abandonados['Dias_Desde_Recogida'] > 30]

        # Si hay pedidos abandonados, los mostramos
        if not pedidos_abandonados.empty:
            st.subheader("Lista de pedidos que superan el mes en el local")
            st.warning("⚠️ Estos pedidos han sido recogidos del proveedor pero no por el cliente.", icon="🚨")
            
            # Limpiamos las columnas de IDs que no necesitamos
            if 'Cliente_id' in pedidos_abandonados.columns:
                pedidos_abandonados = pedidos_abandonados.drop(columns=['Cliente_id'])
            if 'Articulo_id' in pedidos_abandonados.columns:
                pedidos_abandonados = pedidos_abandonados.drop(columns=['Articulo_id'])
            
            # Formateamos las fechas antes de mostrar el DataFrame para que se vean bien
            for col in ['Entrega_Cliente', 'Limite', 'Entrega_Proveedor', 'Recogida_Proveedor', 'Recogida_Cliente']:
                if col in pedidos_abandonados.columns:
                    pedidos_abandonados[col] = pd.to_datetime(pedidos_abandonados[col], errors='coerce').dt.strftime('%Y-%m-%d')


            st.dataframe(pedidos_abandonados.sort_values(by='Recogida_Proveedor'))
        else:
            # Mensaje cuando no hay pedidos abandonados
            st.success("¡No hay pedidos abandonados! Todos los pedidos han sido recogidos a tiempo. 🎉")
else:
        st.info("La tabla de pedidos está vacía. No hay datos para verificar.")