import streamlit as st
import functions as f
import pandas as pd
from streamlit_calendar import calendar


st.markdown("# Limite")
st.markdown("---")

    # Cargar la tabla de pedidos
pedidos = f.get_orders_data()
clientes = f.get_clients_data()
articulos = f.get_articles_data()

if not pedidos.empty:
        # Filtramos solo los pedidos que tienen una fecha límite
        pedidos_join = f.ordersJoin(pedidos, clientes, articulos)
        pedidos_con_limite = pedidos_join[(pedidos_join['Limite'].notna()) & (pedidos_join['Recogida_Cliente'].isna())].copy()

        if not pedidos_con_limite.empty:
            # Convertir la columna 'Limite' a formato de fecha y hora ISO 8601
            pedidos_con_limite['Limite'] = pd.to_datetime(pedidos_con_limite['Limite'], errors='coerce')
            
            # Formato de evento para el calendario
            calendar_events = []
            for index, row in pedidos_con_limite.iterrows():
                event = {
                    "title": f"{row['Cliente']} - {row['Articulo']}",
                    "start": row['Limite'].isoformat(),
                    "end": row['Limite'].isoformat(), # Un evento de una hora
                    #"allDay" : True,

                }
                calendar_events.append(event)
            
            # Opciones del calendario. Quitamos las opciones de 'resource' que son para recursos
            calendar_options = {
                "editable": False,
                "selectable": True,
                "headerToolbar": {
                    "left": "prev,next",
                    "center": "title",
                    "right": "",
                },
                "initialView": "dayGridMonth", # Vista inicial por mes
            }

            calendar_output = calendar(
                events=calendar_events,
                options=calendar_options,
                custom_css="""
                    .fc-event-title {
                        font-weight: 700;
                        white-space: normal;
                        font-size: 0.9em;
                    }
                    .fc-event-time {
                        display: none !important;
                    }
                    .fc-toolbar-title {
                        font-size: 2rem;
                    }
                """,
                key='calendar',
            )

            #st.write(calendar_output) # Muestra el output del calendario, que puede ser la selección del usuario
        else:
            st.info("No hay pedidos con fecha límite para mostrar.")
else:
        st.info("La tabla de pedidos está vacía.")