"""
Sesión mejorada para conexión con Tabula Cloud API.

Proporciona funcionalidad robusta para comunicación HTTP con la API,
incluyendo autenticación, manejo de errores, reintentos automáticos,
y cache de respuestas.
"""

import json
import time
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from ..utils.commons import get_system_info


class Session:
    """
    Sesión mejorada para comunicación con Tabula Cloud API.

    Incluye características como:
    - Autenticación automática con API key
    - Reintentos automáticos con backoff exponencial
    - Manejo robusto de errores HTTP
    - Headers personalizables
    - Timeout configurable
    - Rate limiting
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.tabula.com.py",
        version: str = "v1",
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.3,
        user_agent: str = None,
    ):
        """
        Inicializa la sesión con Tabula Cloud API.

        Args:
            api_key: API key para autenticación
            base_url: URL base de la API
            version: Versión de la API
            timeout: Timeout en segundos para las peticiones
            max_retries: Número máximo de reintentos
            backoff_factor: Factor de backoff para reintentos
            user_agent: User agent personalizado
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.version = version
        self.timeout = timeout

        # Crear sesión de requests personalizada
        self.session = requests.Session()

        # Configurar headers por defecto
        self._setup_headers(user_agent)

        # Configurar reintentos automáticos
        self._setup_retries(max_retries, backoff_factor)

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms entre requests

        # Cache simple de respuestas
        self._response_cache = {}
        self.cache_enabled = False

    def _setup_headers(self, user_agent: str = None) -> None:
        """Configura los headers por defecto de la sesión."""
        if not user_agent:
            system_info = get_system_info()
            user_agent = (
                f"TabulaCloudSync/1.0.0 "
                f"({system_info['system']} {system_info['release']}) "
                f"Python/{system_info['python_version'].split()[0]}"
            )

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": user_agent,
                "X-Client-Version": "1.0.0",
            }
        )

    def _setup_retries(self, max_retries: int, backoff_factor: float) -> None:
        """Configura la estrategia de reintentos."""
        retry_strategy = Retry(
            total=max_retries,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=[
                "HEAD",
                "GET",
                "PUT",
                "DELETE",
                "OPTIONS",
                "TRACE",
            ],
            backoff_factor=backoff_factor,
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _get_full_url(self, endpoint: str) -> str:
        """
        Construye la URL completa para un endpoint.

        Args:
            endpoint: Endpoint de la API

        Returns:
            URL completa
        """
        # Remover barra inicial si existe
        endpoint = endpoint.lstrip("/")

        # Construir URL con versión
        if self.version:
            full_path = f"api/{self.version}/{endpoint}"
        else:
            full_path = f"api/{endpoint}"

        return urljoin(f"{self.base_url}/", full_path)

    def _rate_limit(self) -> None:
        """Aplica rate limiting entre requests."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _handle_response(self, response: requests.Response) -> requests.Response:
        """
        Maneja la respuesta HTTP y errores.

        Args:
            response: Respuesta HTTP

        Returns:
            Respuesta HTTP si es exitosa

        Raises:
            ValueError: Si hay error en la respuesta
        """
        try:
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError:
            error_msg = self._get_error_message(response)
            raise ValueError(error_msg)

    def _get_error_message(self, response: requests.Response) -> str:
        """
        Extrae mensaje de error descriptivo de la respuesta.

        Args:
            response: Respuesta HTTP con error

        Returns:
            Mensaje de error descriptivo
        """
        status_code = response.status_code

        # Intentar extraer mensaje de error del JSON
        try:
            error_data = response.json()
            if "error" in error_data:
                return f"Error {status_code}: {error_data['error']}"
            elif "message" in error_data:
                return f"Error {status_code}: {error_data['message']}"
            elif "detail" in error_data:
                return f"Error {status_code}: {error_data['detail']}"
        except (json.JSONDecodeError, ValueError):
            pass

        # Mensajes por defecto según el código de estado
        error_messages = {
            400: "Solicitud incorrecta. Verifica los datos proporcionados",
            401: "No autorizado. Verifica tu API key",
            403: "Acceso denegado. Permisos insuficientes",
            404: "Recurso no encontrado",
            405: "Método no permitido",
            409: "Conflicto. El recurso ya existe",
            422: "Datos de entrada no válidos",
            429: "Demasiadas solicitudes. Inténtalo más tarde",
            500: "Error interno del servidor",
            502: "Puerta de enlace incorrecta",
            503: "Servicio no disponible",
            504: "Tiempo de espera agotado",
        }

        return error_messages.get(status_code, f"Error HTTP {status_code}")

    def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        use_cache: bool = False,
        **kwargs,
    ) -> requests.Response:
        """
        Realiza una petición GET.

        Args:
            endpoint: Endpoint de la API
            params: Parámetros de query string
            headers: Headers adicionales
            use_cache: Si usar cache para esta petición
            **kwargs: Argumentos adicionales para requests

        Returns:
            Respuesta HTTP
        """
        self._rate_limit()

        url = self._get_full_url(endpoint)

        # Verificar cache
        cache_key = f"GET_{url}_{json.dumps(params, sort_keys=True)}"
        if use_cache and self.cache_enabled and cache_key in self._response_cache:
            return self._response_cache[cache_key]

        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.get(
                url,
                params=params,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs,
            )

            response = self._handle_response(response)

            # Guardar en cache si está habilitado
            if use_cache and self.cache_enabled:
                self._response_cache[cache_key] = response

            return response

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error en petición GET a {url}: {str(e)}")

    def post(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Realiza una petición POST.

        Args:
            endpoint: Endpoint de la API
            data: Datos para enviar como form data
            json_data: Datos para enviar como JSON
            headers: Headers adicionales
            **kwargs: Argumentos adicionales para requests

        Returns:
            Respuesta HTTP
        """
        self._rate_limit()

        url = self._get_full_url(endpoint)

        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.post(
                url,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs,
            )

            return self._handle_response(response)

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error en petición POST a {url}: {str(e)}")

    def put(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Realiza una petición PUT.

        Args:
            endpoint: Endpoint de la API
            data: Datos para enviar como form data
            json_data: Datos para enviar como JSON
            headers: Headers adicionales
            **kwargs: Argumentos adicionales para requests

        Returns:
            Respuesta HTTP
        """
        self._rate_limit()

        url = self._get_full_url(endpoint)

        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.put(
                url,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs,
            )

            return self._handle_response(response)

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error en petición PUT a {url}: {str(e)}")

    def patch(
        self,
        endpoint: str,
        data: Optional[Union[Dict[str, Any], str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Realiza una petición PATCH.

        Args:
            endpoint: Endpoint de la API
            data: Datos para enviar como form data
            json_data: Datos para enviar como JSON
            headers: Headers adicionales
            **kwargs: Argumentos adicionales para requests

        Returns:
            Respuesta HTTP
        """
        self._rate_limit()

        url = self._get_full_url(endpoint)

        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.patch(
                url,
                data=data,
                json=json_data,
                headers=request_headers,
                timeout=self.timeout,
                **kwargs,
            )

            return self._handle_response(response)

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error en petición PATCH a {url}: {str(e)}")

    def delete(
        self, endpoint: str, headers: Optional[Dict[str, str]] = None, **kwargs
    ) -> requests.Response:
        """
        Realiza una petición DELETE.

        Args:
            endpoint: Endpoint de la API
            headers: Headers adicionales
            **kwargs: Argumentos adicionales para requests

        Returns:
            Respuesta HTTP
        """
        self._rate_limit()

        url = self._get_full_url(endpoint)

        # Merge headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        try:
            response = self.session.delete(
                url, headers=request_headers, timeout=self.timeout, **kwargs
            )

            return self._handle_response(response)

        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error en petición DELETE a {url}: {str(e)}")

    def set_api_key(self, api_key: str) -> None:
        """
        Actualiza la API key.

        Args:
            api_key: Nueva API key
        """
        self.api_key = api_key
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    def enable_cache(self) -> None:
        """Habilita el cache de respuestas."""
        self.cache_enabled = True

    def disable_cache(self) -> None:
        """Deshabilita el cache de respuestas."""
        self.cache_enabled = False
        self._response_cache.clear()

    def clear_cache(self) -> None:
        """Limpia el cache de respuestas."""
        self._response_cache.clear()

    def set_rate_limit(self, min_interval_seconds: float) -> None:
        """
        Configura el intervalo mínimo entre peticiones.

        Args:
            min_interval_seconds: Intervalo mínimo en segundos
        """
        self.min_request_interval = min_interval_seconds

    def health_check(self) -> bool:
        """
        Verifica la conectividad con la API.

        Returns:
            True si la API está disponible
        """
        try:
            response = self.get("health", use_cache=False)
            return response.status_code == 200
        except Exception:
            return False

    def get_api_info(self) -> Dict[str, Any]:
        """
        Obtiene información de la API.

        Returns:
            Información de la API
        """
        try:
            response = self.get("info")
            return response.json()
        except Exception:
            return {
                "base_url": self.base_url,
                "version": self.version,
                "status": "unknown",
            }
