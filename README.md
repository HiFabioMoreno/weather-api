# Weather API - OpenWeather Consumer

API REST en Flask que consume la OpenWeather API para obtener información del clima en tiempo real.

## 🚀 Características

- ✅ **GET /health** - Verificar estado de la API
- ✅ **GET /** - Documentación de endpoints
- ✅ **GET /weather** - Obtener clima por ciudad o coordenadas
- ✅ **POST /weather/multiple** - Obtener clima de múltiples ciudades
- ✅ **Validaciones** - Parámetros y coordenadas validadas
- ✅ **Manejo de errores** - 401, 404, timeout, conexión
- ✅ **Respuesta JSON limpia** - Datos formateados y estructurados
- ✅ **Configuración vía .env** - Variables de entorno seguras

## 📋 Requisitos

- Python 3.7+
- Flask 3.0.0
- requests 2.31.0
- python-dotenv 1.0.0

## 🔧 Instalación

1. **Clonar el repositorio**
```bash
cd weather-api
```

2. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

3. **Configurar API Key**
   - Obtén tu API Key en [openweathermap.org](https://openweathermap.org/api)
   - Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```
   - Edita `.env` y reemplaza `your_openwatherapi_key` con tu API Key real

4. **Ejecutar la aplicación**
```bash
python app.py
```

La API estará disponible en `http://localhost:5000`

## 📚 Endpoints

### 1. GET /health
Verifica que la API está funcionando.

**Respuesta exitosa (200):**
```json
{
  "status": "healthy",
  "timestamp": "2026-06-02T15:30:45.123456Z"
}
```

**Respuesta con error (503):**
```json
{
  "status": "unhealthy",
  "message": "API key de OpenWeather no configurada"
}
```

### 2. GET /
Obtiene información sobre la API y sus endpoints disponibles.

**Respuesta (200):**
```json
{
  "message": "Weather API - OpenWeather API Consumer",
  "version": "1.0.0",
  "endpoints": {
    "GET /health": "Verificar estado de la API",
    "GET /weather": "Obtener clima por ciudad o coordenadas",
    "POST /weather/multiple": "Obtener clima de múltiples ciudades"
  }
}
```

### 3. GET /weather
Obtiene el clima para una ubicación específica.

**Parámetros de consulta:**
- `city` (opcional) - Nombre de la ciudad
- `lat` (opcional) - Latitud (-90 a 90)
- `lon` (opcional) - Longitud (-180 a 180)

**Nota:** Proporciona `city` O ambos `lat` y `lon`, no ambos.

**Ejemplos:**

#### Por ciudad:
```bash
curl "http://localhost:5000/weather?city=Madrid"
```

#### Por coordenadas:
```bash
curl "http://localhost:5000/weather?lat=40.4168&lon=-3.7038"
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "data": {
    "city": "Madrid",
    "country": "ES",
    "coordinates": {
      "latitude": 40.4168,
      "longitude": -3.7038
    },
    "weather": {
      "main": "Clear",
      "description": "clear sky",
      "icon": "01d"
    },
    "temperature": {
      "current": 22.5,
      "feels_like": 21.8,
      "min": 20.1,
      "max": 25.3
    },
    "humidity": 65,
    "pressure": 1013,
    "wind": {
      "speed": 3.5,
      "degree": 230
    },
    "clouds": 10,
    "timestamp": "2026-06-02T15:30:45Z"
  }
}
```

**Errores:**

Ciudad no encontrada (404):
```json
{
  "error": "Ciudad no encontrada (404)"
}
```

Parámetros inválidos (400):
```json
{
  "error": "Parámetro inválido",
  "details": "Latitud debe estar entre -90 y 90"
}
```

### 4. POST /weather/multiple
Obtiene el clima para múltiples ciudades.

**Body JSON:**
```json
{
  "cities": ["Madrid", "Barcelona", "Valencia"]
}
```

**Validaciones:**
- Máximo 10 ciudades por solicitud
- Lista no vacía

**Ejemplos:**

```bash
curl -X POST http://localhost:5000/weather/multiple \
  -H "Content-Type: application/json" \
  -d '{
    "cities": ["Madrid", "Barcelona", "New York"]
  }'
```

**Respuesta exitosa (200):**
```json
{
  "success": true,
  "total_requested": 3,
  "total_success": 3,
  "total_errors": 0,
  "data": [
    {
      "city": "Madrid",
      "data": {
        "city": "Madrid",
        "country": "ES",
        "coordinates": { ... },
        "weather": { ... },
        "temperature": { ... },
        "humidity": 65,
        "pressure": 1013,
        "wind": { ... },
        "clouds": 10,
        "timestamp": "2026-06-02T15:30:45Z"
      }
    },
    {
      "city": "Barcelona",
      "data": { ... }
    }
  ],
  "errors": null
}
```

**Con errores parciales:**
```json
{
  "success": true,
  "total_requested": 4,
  "total_success": 3,
  "total_errors": 1,
  "data": [
    { "city": "Madrid", "data": { ... } },
    { "city": "Barcelona", "data": { ... } },
    { "city": "New York", "data": { ... } }
  ],
  "errors": [
    {
      "city": "CiudadInvalida",
      "error": "Ciudad no encontrada (404)"
    }
  ]
}
```

## ⚠️ Manejo de Errores

### Códigos de error HTTP:

| Código | Descripción | Causa |
|--------|-------------|-------|
| 400 | Bad Request | Parámetros inválidos |
| 401 | Unauthorized | API Key inválida |
| 404 | Not Found | Endpoint o ciudad no encontrada |
| 405 | Method Not Allowed | Método HTTP incorrecto |
| 429 | Too Many Requests | Límite de solicitudes excedido |
| 500 | Internal Server Error | Error en servidor |
| 503 | Service Unavailable | Error de API Key o conexión |

### Errores de conexión:

- **Timeout** - La solicitud tardó más de 5 segundos
- **ConnectionError** - No se pudo conectar a OpenWeather
- **RequestException** - Error genérico en la solicitud

## 🔐 Variables de Entorno

Archivo `.env`:
```env
# API Key de OpenWeatherMap
OPENWEATHER_API_KEY=your_actual_api_key

# Entorno de Flask
FLASK_ENV=development

# Debug (True/False)
FLASK_DEBUG=False

# Puerto
PORT=5000
```

## 🐳 Docker

Para ejecutar con Docker:

```bash
docker build -t weather-api .
docker run -p 5000:5000 --env-file .env weather-api
```

## 📝 Ejemplos de uso con Python

```python
import requests

BASE_URL = "http://localhost:5000"

# 1. Verificar salud
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 2. Obtener clima por ciudad
response = requests.get(f"{BASE_URL}/weather?city=Madrid")
print(response.json())

# 3. Obtener clima por coordenadas
response = requests.get(f"{BASE_URL}/weather?lat=40.4168&lon=-3.7038")
print(response.json())

# 4. Obtener clima de múltiples ciudades
response = requests.post(
    f"{BASE_URL}/weather/multiple",
    json={"cities": ["Madrid", "Barcelona", "Valencia"]}
)
print(response.json())
```

## 🧪 Pruebas con cURL

```bash
# Health check
curl http://localhost:5000/health

# Documentación
curl http://localhost:5000/

# Clima por ciudad
curl "http://localhost:5000/weather?city=London"

# Clima por coordenadas
curl "http://localhost:5000/weather?lat=51.5074&lon=-0.1278"

# Múltiples ciudades
curl -X POST http://localhost:5000/weather/multiple \
  -H "Content-Type: application/json" \
  -d '{"cities": ["Paris", "Berlin", "Amsterdam"]}'
```

## 📊 Estructura de respuesta

Todas las respuestas tienen estructura JSON:
- `success`: Booleano indicando éxito
- `data`: Objeto con los datos del clima
- `error`: Mensaje de error (si aplica)
- `details`: Detalles adicionales del error

Datos del clima incluyen:
- Información de ubicación (ciudad, país, coordenadas)
- Estado del clima (descripción, ícono)
- Temperaturas (actual, sensación térmica, mín/máx)
- Humedad y presión
- Viento (velocidad, dirección)
- Nubosidad
- Timestamp UTC

## 🛠️ Desarrollo

### Estructura del código

- **Validaciones**: `validate_api_key()`, `validate_coordinates()`, `validate_city()`
- **Funciones auxiliares**: `fetch_weather()`, `format_weather_response()`
- **Endpoints**: `/health`, `/`, `/weather`, `/weather/multiple`
- **Manejo de errores**: Handlers para 404, 405, 500

### Configuración

- Timeout: 5 segundos
- Unidades: Métrica (Celsius)
- Máximo ciudades simultáneas: 10

## 📄 Licencia

MIT

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o PR.
