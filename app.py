import os
import requests
from datetime import datetime
from flask import Flask, jsonify, request
from dotenv import load_dotenv
from requests.exceptions import Timeout, ConnectionError, RequestException

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configuración
OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY')
OPENWEATHER_BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'
FORECAST_BASE_URL = 'https://api.openweathermap.org/data/2.5/forecast'
REQUEST_TIMEOUT = 5


# ==================== Validaciones ====================

def validate_api_key():
    """Valida que la API key esté configurada."""
    if not OPENWEATHER_API_KEY:
        return False, "API key de OpenWeather no configurada"
    return True, None


def validate_coordinates(lat, lon):
    """Valida que las coordenadas sean válidas."""
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90):
            return False, "Latitud debe estar entre -90 y 90"
        if not (-180 <= lon <= 180):
            return False, "Longitud debe estar entre -180 y 180"
        return True, (lat, lon)
    except (ValueError, TypeError):
        return False, "Coordenadas inválidas"


def validate_city(city):
    """Valida que el nombre de ciudad no esté vacío."""
    if not city or not isinstance(city, str) or not city.strip():
        return False, "Nombre de ciudad inválido"
    return True, city.strip()


# ==================== Funciones auxiliares ====================

def fetch_weather(query_params):
    """
    Consume OpenWeather API con parámetros dados.
    
    Args:
        query_params: dict con parámetros para la API
    
    Returns:
        tuple: (success: bool, data: dict or error_message: str)
    """
    try:
        query_params['appid'] = OPENWEATHER_API_KEY
        query_params['units'] = 'metric'  # Temperatura en Celsius
        
        response = requests.get(
            OPENWEATHER_BASE_URL,
            params=query_params,
            timeout=REQUEST_TIMEOUT
        )
        
        # Manejo de errores HTTP
        if response.status_code == 401:
            return False, "API key inválida (401)"
        elif response.status_code == 404:
            return False, "Ciudad no encontrada (404)"
        elif response.status_code == 429:
            return False, "Límite de solicitudes excedido (429)"
        elif response.status_code >= 500:
            return False, "Error en servidor de OpenWeather (500)"
        
        response.raise_for_status()
        return True, response.json()
        
    except Timeout:
        return False, "Timeout: OpenWeather API tardó demasiado en responder"
    except ConnectionError:
        return False, "Error de conexión: No se pudo conectar a OpenWeather"
    except RequestException as e:
        return False, f"Error en solicitud: {str(e)}"
    except Exception as e:
        return False, f"Error inesperado: {str(e)}"


def format_weather_response(data):
    """
    Formatea la respuesta de OpenWeather a un formato limpio.
    
    Args:
        data: dict con datos de OpenWeather
    
    Returns:
        dict: datos formateados
    """
    return {
        'city': data.get('name', 'Desconocida'),
        'country': data.get('sys', {}).get('country', ''),
        'coordinates': {
            'latitude': data.get('coord', {}).get('lat'),
            'longitude': data.get('coord', {}).get('lon')
        },
        'weather': {
            'main': data.get('weather', [{}])[0].get('main', 'Desconocido'),
            'description': data.get('weather', [{}])[0].get('description', ''),
            'icon': data.get('weather', [{}])[0].get('icon', '')
        },
        'temperature': {
            'current': data.get('main', {}).get('temp'),
            'feels_like': data.get('main', {}).get('feels_like'),
            'min': data.get('main', {}).get('temp_min'),
            'max': data.get('main', {}).get('temp_max')
        },
        'humidity': data.get('main', {}).get('humidity'),
        'pressure': data.get('main', {}).get('pressure'),
        'wind': {
            'speed': data.get('wind', {}).get('speed'),
            'degree': data.get('wind', {}).get('deg')
        },
        'clouds': data.get('clouds', {}).get('all'),
        'timestamp': datetime.utcfromtimestamp(
            data.get('dt', 0)
        ).isoformat() + 'Z'
    }


# ==================== Endpoints ====================

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint para verificar que la API está funcionando.
    
    Returns:
        JSON con estado de salud
    """
    is_valid, error = validate_api_key()

    return jsonify({
        'status': 'healthy' if is_valid else 'degraded',
        'openweather_api_key_configured': bool(is_valid),
        'message': None if is_valid else error,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200


@app.route('/', methods=['GET'])
def index():
    """
    Endpoint raíz con información sobre la API.
    
    Returns:
        JSON con documentación de endpoints
    """
    return jsonify({
        'message': 'Weather API - OpenWeather API Consumer',
        'version': '1.0.0',
        'endpoints': {
            'GET /health': 'Verificar estado de la API',
            'GET /weather': 'Obtener clima por ciudad o coordenadas. Parámetros: ?city=<ciudad> OR ?lat=<latitud>&lon=<longitud>',
            'POST /weather/multiple': 'Obtener clima de múltiples ciudades. Body: {"cities": ["ciudad1", "ciudad2", ...]}'
        }
    }), 200


@app.route('/weather', methods=['GET'])
def get_weather():
    """
    Obtiene información del clima para una ubicación.
    
    Query params:
        - city: nombre de la ciudad
        - lat, lon: coordenadas (ambos requeridos)
    
    Returns:
        JSON con datos del clima
    """
    is_valid, error = validate_api_key()
    if not is_valid:
        return jsonify({'error': error}), 503
    
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    # Validar parámetros
    if city:
        is_valid, city = validate_city(city)
        if not is_valid:
            return jsonify({
                'error': 'Parámetro inválido',
                'details': city
            }), 400
        query_params = {'q': city}
    elif lat and lon:
        is_valid, coords = validate_coordinates(lat, lon)
        if not is_valid:
            return jsonify({
                'error': 'Parámetro inválido',
                'details': coords
            }), 400
        query_params = {'lat': coords[0], 'lon': coords[1]}
    else:
        return jsonify({
            'error': 'Parámetros requeridos',
            'details': 'Proporcione ?city=<ciudad> O ?lat=<latitud>&lon=<longitud>'
        }), 400
    
    # Consumir API
    success, data = fetch_weather(query_params)
    
    if not success:
        status_code = 404 if 'no encontrada' in data.lower() else 400
        return jsonify({'error': data}), status_code
    
    return jsonify({
        'success': True,
        'data': format_weather_response(data)
    }), 200


@app.route('/weather/multiple', methods=['POST'])
def get_multiple_weather():
    """
    Obtiene información del clima para múltiples ciudades.
    
    Body JSON:
        {
            "cities": ["ciudad1", "ciudad2", ...]
        }
    
    Returns:
        JSON con datos de clima de todas las ciudades
    """
    is_valid, error = validate_api_key()
    if not is_valid:
        return jsonify({'error': error}), 503
    
    data = request.get_json()
    
    # Validar que se envió JSON
    if not data:
        return jsonify({
            'error': 'Solicitud inválida',
            'details': 'Se requiere JSON en el body'
        }), 400
    
    cities = data.get('cities', [])
    
    # Validar que cities es una lista
    if not isinstance(cities, list) or len(cities) == 0:
        return jsonify({
            'error': 'Parámetro inválido',
            'details': 'Se requiere "cities" como lista no vacía'
        }), 400
    
    # Validar máximo 10 ciudades
    if len(cities) > 10:
        return jsonify({
            'error': 'Demasiadas ciudades',
            'details': 'Máximo 10 ciudades por solicitud'
        }), 400
    
    results = []
    errors = []
    
    # Obtener clima para cada ciudad
    for city in cities:
        is_valid, city_clean = validate_city(city)
        
        if not is_valid:
            errors.append({
                'city': city,
                'error': city_clean
            })
            continue
        
        success, response_data = fetch_weather({'q': city_clean})
        
        if not success:
            errors.append({
                'city': city_clean,
                'error': response_data
            })
        else:
            results.append({
                'city': city_clean,
                'data': format_weather_response(response_data)
            })
    
    return jsonify({
        'success': True,
        'total_requested': len(cities),
        'total_success': len(results),
        'total_errors': len(errors),
        'data': results,
        'errors': errors if errors else None
    }), 200


# ==================== Manejo de errores ====================

@app.errorhandler(404)
def not_found(error):
    """Manejo de rutas no encontradas."""
    return jsonify({
        'error': 'Endpoint no encontrado',
        'status': 404
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Manejo de método HTTP no permitido."""
    return jsonify({
        'error': 'Método HTTP no permitido',
        'status': 405
    }), 405


@app.errorhandler(500)
def internal_error(error):
    """Manejo de errores internos del servidor."""
    return jsonify({
        'error': 'Error interno del servidor',
        'status': 500
    }), 500


# ==================== Punto de entrada ====================

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )

