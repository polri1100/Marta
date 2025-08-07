import streamlit as st
import functions as f
import pandas as pd


st.markdown("# Contabilidad 📊")
st.markdown("---")

pedidos_df = f.obtainTable("Pedidos")

if not pedidos_df.empty:
        # Hacemos una copia del DataFrame para trabajar con ella
        analisis_df = pedidos_df.copy()
        
        # Convertir la columna 'Fecha_Pedido' a formato de fecha
        analisis_df['Recogida_Cliente'] = pd.to_datetime(analisis_df['Recogida_Cliente'], errors='coerce')
        
        # Eliminar filas con fechas no válidas
        analisis_df = analisis_df.dropna(subset=['Recogida_Cliente'])
        
        if not analisis_df.empty:

            analisis_df['Recogida_Cliente'] = analisis_df['Recogida_Cliente'].dt.strftime('%Y-%m-%d')

            # Agrupar los datos por fecha y sumar 'Importe' y 'Coste_Proveedor'
            #analisis_df = analisis_df.groupby('Entrega_Cliente')[['Importe', 'Coste_Proveedor']].sum().reset_index()
            
            # Asegurarse de que las columnas numéricas sean de tipo numérico
            analisis_df['Importe'] = pd.to_numeric(analisis_df['Importe'], errors='coerce').fillna(0)
            if 'Coste_Material' in analisis_df.columns:
                analisis_df['Coste_Material'] = pd.to_numeric(analisis_df['Coste_Material'], errors='coerce').fillna(0)
            else:
                analisis_df['Coste_Material'] = 0
            analisis_df['Coste_Proveedor'] = pd.to_numeric(analisis_df['Coste_Proveedor'], errors='coerce').fillna(0)

            analisis_df_grouped = analisis_df.groupby('Recogida_Cliente').agg(
                Pedidos_del_dia=('ID', 'count'),
                Importe=('Importe', 'sum'),
                Coste_Proveedor=('Coste_Proveedor', 'sum'),
                Coste_Material=('Coste_Material', 'sum')
            ).reset_index()

            analisis_df_grouped['Coste_Total'] = analisis_df_grouped['Coste_Proveedor'] + analisis_df_grouped['Coste_Material']
            analisis_df_grouped['Margen'] = (analisis_df_grouped['Importe'] - analisis_df_grouped['Coste_Total']) / analisis_df_grouped['Importe']
            
            analisis_df_grouped['Margen'] = analisis_df_grouped['Margen'].apply(lambda x: f"{x:.2%}")

            st.markdown("### Evolución diaria de Ingresos y Costes")
            
            # Preparamos los datos para el gráfico de barras agrupadas de Altair
            chart_data = analisis_df_grouped.melt(
                id_vars=['Recogida_Cliente'],
                value_vars=['Importe', 'Coste_Total'],
                var_name='Tipo',
                value_name='Valor'
            )
            
            # --- SOLUCIÓN CORRECTA: USAR st.bar_chart con stack=False ---
            st.bar_chart(
                chart_data,
                x='Recogida_Cliente',
                y='Valor',
                color='Tipo',
                stack=False,
                use_container_width=True,
            )
            
            # Mostramos la tabla de datos del análisis
            st.markdown("### Tabla de datos del análisis")
            st.dataframe(analisis_df_grouped)
        else:
            st.warning("La tabla de pedidos no contiene fechas válidas.")
else:
        st.warning("No hay datos en la tabla de pedidos para analizar.")



