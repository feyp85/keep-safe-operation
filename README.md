# Keep Safe Operation

Aplicación para generar recomendaciones operativas personalizadas para fumigación agrícola con dron DJI Agras T50.

## Funciones principales

- Gestión de clientes con ubicación georreferenciada
- Ingreso de datos de cultivo, hectáreas y dilución
- Cálculo de volumen de solución, vuelos y tiempo estimado
- Recomendaciones técnicas para el operador del dron
- Registro de operaciones en Google Sheets
- Interfaz interactiva con mapa (usando folium)

## Cómo ejecutar localmente

1. Instala las dependencias:
```bash
pip install -r requirements.txt
```

2. Coloca tu archivo de credenciales de Google (`.json`) como secreto en `.streamlit/secrets.toml`.

3. Ejecuta la app:
```bash
streamlit run app.py
```

## Requisitos

- Python 3.8+
- Cuenta de Google con acceso a una hoja de cálculo llamada `KeepSafe_DB`

## Créditos

Desarrollado por Keep Safe.
