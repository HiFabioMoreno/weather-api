"""
Script de prueba para Weather API
Ejecutar: python test.py
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:5000"
HEADERS = {"Content-Type": "application/json"}

# Colores para output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_result(test_name, success, response_data=None, error=None):
    """Imprime resultado de prueba."""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if success else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"\n{status} | {test_name}")
    if response_data:
        print(f"  Response: {json.dumps(response_data, indent=2)[:200]}...")
    if error:
        print(f"  Error: {error}")

def test_health():
    """Test GET /health"""
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        success = response.status_code == 200 and response.json().get('status') == 'healthy'
        print_result("GET /health", success, response.json())
        return success
    except Exception as e:
        print_result("GET /health", False, error=str(e))
        return False

def test_index():
    """Test GET /"""
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        success = response.status_code == 200 and 'endpoints' in response.json()
        print_result("GET /", success, response.json())
        return success
    except Exception as e:
        print_result("GET /", False, error=str(e))
        return False

def test_weather_by_city():
    """Test GET /weather?city=..."""
    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={"city": "Madrid"},
            timeout=5
        )
        data = response.json()
        success = response.status_code == 200 and data.get('success') and 'data' in data
        print_result("GET /weather?city=Madrid", success, data)
        return success
    except Exception as e:
        print_result("GET /weather?city=Madrid", False, error=str(e))
        return False

def test_weather_by_coordinates():
    """Test GET /weather?lat=...&lon=..."""
    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={"lat": "40.4168", "lon": "-3.7038"},
            timeout=5
        )
        data = response.json()
        success = response.status_code == 200 and data.get('success') and 'data' in data
        print_result("GET /weather?lat=40.4168&lon=-3.7038", success, data)
        return success
    except Exception as e:
        print_result("GET /weather?lat=40.4168&lon=-3.7038", False, error=str(e))
        return False

def test_weather_invalid_coordinates():
    """Test GET /weather con coordenadas inválidas"""
    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={"lat": "100", "lon": "-3.7038"},
            timeout=5
        )
        success = response.status_code == 400
        data = response.json()
        print_result("GET /weather (coords inválidas)", success, data)
        return success
    except Exception as e:
        print_result("GET /weather (coords inválidas)", False, error=str(e))
        return False

def test_weather_no_params():
    """Test GET /weather sin parámetros"""
    try:
        response = requests.get(f"{BASE_URL}/weather", timeout=5)
        success = response.status_code == 400
        data = response.json()
        print_result("GET /weather (sin parámetros)", success, data)
        return success
    except Exception as e:
        print_result("GET /weather (sin parámetros)", False, error=str(e))
        return False

def test_weather_not_found():
    """Test GET /weather con ciudad que no existe"""
    try:
        response = requests.get(
            f"{BASE_URL}/weather",
            params={"city": "CiudadFantasmaXYZ123"},
            timeout=5
        )
        success = response.status_code == 404
        data = response.json()
        print_result("GET /weather (ciudad no existe)", success, data)
        return success
    except Exception as e:
        print_result("GET /weather (ciudad no existe)", False, error=str(e))
        return False

def test_multiple_weather():
    """Test POST /weather/multiple"""
    try:
        payload = {"cities": ["Madrid", "Barcelona", "Valencia"]}
        response = requests.post(
            f"{BASE_URL}/weather/multiple",
            json=payload,
            headers=HEADERS,
            timeout=10
        )
        data = response.json()
        success = response.status_code == 200 and data.get('success')
        print_result("POST /weather/multiple (3 ciudades)", success, data)
        return success
    except Exception as e:
        print_result("POST /weather/multiple (3 ciudades)", False, error=str(e))
        return False

def test_multiple_weather_no_body():
    """Test POST /weather/multiple sin body"""
    try:
        response = requests.post(
            f"{BASE_URL}/weather/multiple",
            headers=HEADERS,
            timeout=5
        )
        success = response.status_code == 400
        data = response.json()
        print_result("POST /weather/multiple (sin body)", success, data)
        return success
    except Exception as e:
        print_result("POST /weather/multiple (sin body)", False, error=str(e))
        return False

def test_multiple_weather_empty_list():
    """Test POST /weather/multiple con lista vacía"""
    try:
        payload = {"cities": []}
        response = requests.post(
            f"{BASE_URL}/weather/multiple",
            json=payload,
            headers=HEADERS,
            timeout=5
        )
        success = response.status_code == 400
        data = response.json()
        print_result("POST /weather/multiple (lista vacía)", success, data)
        return success
    except Exception as e:
        print_result("POST /weather/multiple (lista vacía)", False, error=str(e))
        return False

def test_multiple_weather_too_many():
    """Test POST /weather/multiple con más de 10 ciudades"""
    try:
        cities = [f"City{i}" for i in range(15)]
        payload = {"cities": cities}
        response = requests.post(
            f"{BASE_URL}/weather/multiple",
            json=payload,
            headers=HEADERS,
            timeout=5
        )
        success = response.status_code == 400
        data = response.json()
        print_result("POST /weather/multiple (>10 ciudades)", success, data)
        return success
    except Exception as e:
        print_result("POST /weather/multiple (>10 ciudades)", False, error=str(e))
        return False

def test_not_found_endpoint():
    """Test endpoint que no existe"""
    try:
        response = requests.get(f"{BASE_URL}/endpoint/inexistente", timeout=5)
        success = response.status_code == 404
        data = response.json()
        print_result("GET /endpoint/inexistente (404)", success, data)
        return success
    except Exception as e:
        print_result("GET /endpoint/inexistente (404)", False, error=str(e))
        return False

def run_all_tests():
    """Ejecuta todas las pruebas."""
    print(f"\n{Colors.BLUE}{'='*60}")
    print("WEATHER API - SUITE DE PRUEBAS")
    print(f"{'='*60}{Colors.END}\n")
    
    print(f"{Colors.YELLOW}Asegúrate de que la API está ejecutándose en {BASE_URL}{Colors.END}")
    print(f"{Colors.YELLOW}Presiona Enter para continuar...{Colors.END}")
    input()
    
    tests = [
        ("Salud", test_health),
        ("Documentación", test_index),
        ("Clima por ciudad", test_weather_by_city),
        ("Clima por coordenadas", test_weather_by_coordinates),
        ("Validación de coordenadas", test_weather_invalid_coordinates),
        ("Sin parámetros", test_weather_no_params),
        ("Ciudad no encontrada", test_weather_not_found),
        ("Múltiples ciudades", test_multiple_weather),
        ("Sin body", test_multiple_weather_no_body),
        ("Lista vacía", test_multiple_weather_empty_list),
        ("Demasiadas ciudades", test_multiple_weather_too_many),
        ("Endpoint no existe", test_not_found_endpoint),
    ]
    
    results = []
    for test_name, test_func in tests:
        results.append(test_func())
        sleep(0.5)  # Pequeño delay entre pruebas
    
    # Resumen
    passed = sum(results)
    total = len(results)
    
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"RESULTADOS: {Colors.GREEN}{passed}/{total}{Colors.END} pruebas pasadas")
    print(f"{'='*60}{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}¡Todas las pruebas pasaron! ✓{Colors.END}\n")
    else:
        print(f"{Colors.RED}Algunas pruebas fallaron. Verifica la API.{Colors.END}\n")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Pruebas canceladas.{Colors.END}\n")
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}\n")
