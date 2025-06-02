
import streamlit as st
import pandas as pd
from PIL import Image
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import json
import folium
from streamlit_folium import st_folium

# Google Sheets auth
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = json.loads(st.secrets["GOOGLE_CREDENTIALS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
try:
    sheet = client.open("KeepSafe_DB")
except gspread.exceptions.APIError:
    st.error("⚠️ No se pudo acceder al documento 'KeepSafe_DB'. Verifica que el Service Account tenga permiso de editor en Google Sheets.")
    st.stop()
clientes_ws = sheet.worksheet("Clientes")
operaciones_ws = sheet.worksheet("Operaciones")

# Logo
logo = Image.open("logo1.0.png")
st.image(logo, width=180)

st.title("Keep Safe Operation")
st.markdown("### Hoja de Recomendaciones Operativas para Fumigación con Dron DJI Agras T50")

# Cultivos data
cultivos_data = {
    "Banano": {"tasa_aplicacion": 18, "velocidad": "20-30 km/h", "altura": "7-8 m", "ancho_faja": "7-9.5 m", "gota": "Fina/Media"},
    "Maíz": {"tasa_aplicacion": 19, "velocidad": "20-25 km/h", "altura": "5-6 m", "ancho_faja": "7-8.5 m", "gota": "Fina/Media/Gruesa"},
    "Arroz": {"tasa_aplicacion": 16.5, "velocidad": "25-30 km/h", "altura": "4-7 m", "ancho_faja": "6.5-8 m", "gota": "Muy Fina/Fina/Media"},
    "Cacao": {"tasa_aplicacion": 25, "velocidad": "20-25 km/h", "altura": "7 m", "ancho_faja": "7-8.5 m", "gota": "Muy Fina/Fina/Media"},
}

# Clientes
st.sidebar.subheader("📇 Gestión de Clientes")
try:
    clientes_data = clientes_ws.get_all_records()
except gspread.exceptions.APIError:
    st.error("❌ No se pudo acceder a la hoja de clientes. Verifica permisos o conexión.")
    st.stop()

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

# Crear nuevo cliente
with st.sidebar.expander("➕ Crear nuevo cliente"):
    nuevo_ruc = st.text_input("RUC")
    nombre = st.text_input("Nombre")
    telefono = st.text_input("Teléfono")
    email = st.text_input("Email")
    ubicacion = st.text_input("Ubicación")
    responsable = st.text_input("Responsable Técnico")

    st.markdown("📍 Haz clic en el mapa para seleccionar la ubicación del cliente")
    m = folium.Map(location=[-2.1894, -79.8891], zoom_start=13)
    m.add_child(folium.LatLngPopup())
    map_data = st_folium(m, height=350, width=700)
    lat = map_data["last_clicked"]["lat"] if map_data and map_data["last_clicked"] else -2.1894
    lon = map_data["last_clicked"]["lng"] if map_data and map_data["last_clicked"] else -79.8891
    st.write(f"📌 Latitud seleccionada: {lat:.6f}")
    st.write(f"📌 Longitud seleccionada: {lon:.6f}")

    if st.button("Guardar Cliente"):
        if nuevo_ruc in [c["RUC"] for c in clientes_data]:
            st.error("❌ Este RUC ya está registrado.")
        else:
            fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            clientes_ws.append_row([len(clientes_data)+1, nuevo_ruc, nombre, telefono, email, ubicacion, responsable, lat, lon, fecha])
            st.success("✅ Cliente guardado")

# Recomendaciones
cultivo = st.selectbox("🌿 Cultivo", list(cultivos_data.keys()))
hectareas = st.number_input("📐 Hectáreas", min_value=0.1, step=0.1)
dilucion = st.number_input("🧪 Dilución (%)", min_value=0.0, step=0.1)

# Descripción detallada de la fórmula o mezcla
descripcion_formula = st.text_area(
    "🧪 Descripción técnica de la mezcla a aplicar",
    placeholder="Ejemplo: Glifosato 480 SL a 2 L/ha, diluido en 100 L de agua. Preparado el 01/06/2025. Lote #12345."
)

# Campos adicionales sugeridos
etapa_cultivo = st.selectbox(
    "🌱 Etapa del cultivo",
    ["Seleccionar...", "Siembra", "Vegetativo", "Floración", "Fructificación", "Madurez", "Cosecha"]
)

# Mostrar recomendación según etapa
recomendaciones_etapa = {
    "Siembra": "Evitar aplicaciones con herbicidas residuales cerca de la germinación.",
    "Vegetativo": "Etapa óptima para fertilización foliar y control de plagas tempranas.",
    "Floración": "Evitar insecticidas tóxicos para polinizadores. Aplicar temprano o tarde.",
    "Fructificación": "Priorizar fungicidas preventivos. Mantener cobertura uniforme.",
    "Madurez": "Evitar aplicaciones cercanas a cosecha sin observar el periodo de carencia.",
    "Cosecha": "No se recomienda aplicar productos fitosanitarios en esta etapa."
}

if etapa_cultivo != "Seleccionar...":
    st.info(f"🛈 Recomendación para esta etapa: {recomendaciones_etapa.get(etapa_cultivo, '')}")


tipo_tratamiento = st.selectbox(
    "🧫 Tipo de tratamiento",
    ["Seleccionar...", "Herbicida", "Insecticida", "Fungicida", "Fertilizante", "Biopesticida", "Otro"]
)

condiciones_terreno = st.text_area(
    "⛰️ Condiciones del terreno",
    placeholder="Ej: Terreno plano, con pendiente leve hacia el sur. Obstáculos: árboles dispersos, cables eléctricos en el borde este."
)

condiciones_ambientales = st.text_area(
    "🌤️ Condiciones ambientales esperadas",
    placeholder="Ej: Aplicación entre 06h00 y 08h00. Viento <10 km/h. Temperatura 26°C aprox."
)

# Recomendación automática según tipo de tratamiento
recomendaciones_seguridad = {
    "Insecticida": "Tiempo de reentrada recomendado: 24 horas. Usar señalización visible.",
    "Herbicida": "Tiempo de reentrada recomendado: 12 horas. Evitar contacto directo.",
    "Fertilizante": "Tiempo de reentrada recomendado: 6 horas. Aplicar en horas frescas del día.",
    "Biopesticida": "Tiempo de reentrada recomendado: 4 horas. Bajo riesgo para operarios.",
    "Fungicida": "Tiempo de reentrada recomendado: 12 horas. Asegurar buena ventilación del cultivo.",
    "Otro": "Verificar ficha técnica del producto aplicado."
}

texto_sugerido = recomendaciones_seguridad.get(tipo_tratamiento, "")

seguridad_observaciones = st.text_area(
    "⚠️ Seguridad / Observaciones especiales",
    value=texto_sugerido,
    placeholder="Observaciones específicas según el producto o condiciones del sitio."
)


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
            descripcion_formula, etapa_cultivo, tipo_tratamiento, condiciones_terreno,
            condiciones_ambientales, seguridad_observaciones,
            total_sol, puro, int(vuelos), round(tiempo, 2), velocidad, altura, faja, gota, tasa_aplicacion, now
        ])
        st.success("✅ Operación guardada")
