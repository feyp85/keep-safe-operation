
import streamlit as st
import pandas as pd
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
from streamlit_folium import st_folium
import folium

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open("KeepSafe_DB")
clientes_ws = sheet.worksheet("Clientes")
operaciones_ws = sheet.worksheet("Operaciones")

logo = Image.open("logo1.0.png")
st.image(logo, width=180)

st.title("Keep Safe Operation")
st.markdown("### Hoja de Recomendaciones Operativas para Fumigación con Dron DJI Agras T50")

cultivos_data = {
    "Banano": {"tasa_aplicacion": 18, "velocidad": "20-30 km/h", "altura": "7-8 m", "ancho_faja": "7-9.5 m", "gota": "Fina/Media"},
    "Maíz": {"tasa_aplicacion": 19, "velocidad": "20-25 km/h", "altura": "5-6 m", "ancho_faja": "7-8.5 m", "gota": "Fina/Media/Gruesa"},
    "Arroz": {"tasa_aplicacion": 16.5, "velocidad": "25-30 km/h", "altura": "4-7 m", "ancho_faja": "6.5-8 m", "gota": "Muy Fina/Fina/Media"},
    "Cacao": {"tasa_aplicacion": 25, "velocidad": "20-25 km/h", "altura": "7 m", "ancho_faja": "7-8.5 m", "gota": "Muy Fina/Fina/Media"},
}

st.sidebar.subheader("📇 Gestión de Clientes")
clientes_data = clientes_ws.get_all_records()
lista_rucs = [c["RUC"] for c in clientes_data]
cliente_nombres = [f"{c['RUC']} - {c['Nombre']}" for c in clientes_data]

ruc_input = st.sidebar.selectbox("🔍 Buscar cliente por RUC", options=cliente_nombres)

if ruc_input:
    ruc_codigo = ruc_input.split(" - ")[0]
    cliente_encontrado = next((c for c in clientes_data if c["RUC"] == ruc_codigo), None)
else:
    ruc_codigo = ""
    cliente_encontrado = None

if cliente_encontrado:
    st.sidebar.success(f"Cliente: {cliente_encontrado['Nombre']}")
else:
    st.sidebar.warning("Cliente no encontrado")

with st.sidebar.expander("➕ Crear nuevo cliente"):
    nuevo_ruc = st.text_input("RUC")
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Teléfono")
    email = st.text_input("Email")
    ubicacion = st.text_input("Ubicación")
    responsable = st.text_input("Responsable Técnico")
    
 st.markdown("📍 Haz clic en el mapa para seleccionar ubicación")

    m = folium.Map(location=[-2.1894, -79.8891], zoom_start=13)
    marker = folium.Marker(location=[-2.1894, -79.8891], draggable=True)
    marker.add_to(m)
    output = st_folium(m, height=300, width=600)

    lat = output['last_clicked']['lat'] if output and output.get('last_clicked') else -2.1894
    lon = output['last_clicked']['lng'] if output and output.get('last_clicked') else -79.8891
    selected_location = st.session_state.get("selected_location", default_location)

    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/streets-v12",
        initial_view_state=pdk.ViewState(
            latitude=selected_location["lat"],
            longitude=selected_location["lon"],
            zoom=12,
            pitch=0,
        ),
        layers=[
            pdk.Layer(
                "ScatterplotLayer",
                data=[selected_location],
                get_position='[lon, lat]',
                get_color='[200, 30, 0, 160]',
                get_radius=100,
            )
        ],
    ))

    lat = st.number_input("Latitud", value=selected_location["lat"], format="%.6f")
    lon = st.number_input("Longitud", value=selected_location["lon"], format="%.6f")

    if st.button("Guardar Cliente"):
        if nuevo_ruc in lista_rucs:
            st.error("❌ Este RUC ya está registrado.")
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            clientes_ws.append_row([len(clientes_data)+1, nuevo_ruc, nombre, telefono, email, ubicacion, responsable, lat, lon, fecha])
            st.success("Cliente guardado")

cultivo = st.selectbox("🌿 Cultivo", list(cultivos_data.keys()))
hectareas = st.number_input("📐 Hectáreas", min_value=0.1, step=0.1)
dilucion = st.number_input("🧪 Dilución (%)", min_value=0.0, step=0.1)

if cultivo and hectareas:
    datos = cultivos_data[cultivo]
    tasa = datos["tasa_aplicacion"]
    total_sol = tasa * hectareas
    puro = total_sol * (dilucion / 100)
    vuelos = total_sol / 40
    tiempo = vuelos * 10 / 60

    st.markdown("---")
    st.subheader("📋 Recomendaciones Técnicas - para el operador")
    velocidad = st.text_input(f"🔹 Velocidad (rango sugerido: {datos['velocidad']})")
    altura = st.text_input(f"🔹 Altura (rango sugerido: {datos['altura']})")
    faja = st.text_input(f"🔹 Ancho de faja (rango sugerido: {datos['ancho_faja']})")
    gota = st.text_input(f"🔹 Tamaño de gota (sugerido: {datos['gota']})")
    tasa_aplicacion = st.text_input(f"🔹 Tasa de aplicación (sugerida: {tasa} L/ha)", value=str(tasa))

    st.subheader("🛠️ Cálculos Operativos")
    st.write(f"✅ Solución total: {total_sol:.2f} L")
    st.write(f"✅ Producto puro: {puro:.2f} L")
    st.write(f"✅ Vuelos: {vuelos:.0f}")
    st.write(f"✅ Tiempo estimado: {tiempo:.2f} h")

    if st.button("💾 Guardar Operación"):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        operaciones_ws.append_row([
            len(operaciones_ws.get_all_values()), ruc_codigo, cultivo, hectareas, dilucion,
            total_sol, puro, int(vuelos), round(tiempo, 2), velocidad, altura, faja, gota, tasa_aplicacion, now
        ])
        st.success("Operación guardada")

