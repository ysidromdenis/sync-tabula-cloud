"""Modulo para la gestión de sesiones de conexión con el servidor de Tabula."""

import requests

from core.consts import USER_AGENT
from core.urls import PORT, PROTOCOLO, URL_BASE
from utils.logger import logging


class Session:
    """Sesión de conexión con el servidor de Tabula."""

    def __init__(self, token) -> None:
        """
        Inicializa una sesión de conexión a través de una solicitud POST al servidor.

        :param user: str, nombre de usuario para iniciar sesión
        :param password: str, contraseña del usuario para iniciar sesión
        :param domain: str, nombre de dominio de la URL (opcional)
        :return: None
        :raises ValueError: si se produce un error en la autenticación del usuario
        :raises HTTPError: si se produce un error HTTP no válido en la respuesta
        :raises ConnectionError: si se produce un error de conexión con el servidor
        """
        self.domain = URL_BASE
        logging.info("Este es el dominio: %s", self.domain)
        self.headers = {
            "Authorization": f"Token {token}",
            "Referer": f"{PROTOCOLO}://{self.domain}",
            "User-Agent": USER_AGENT,
        }

    def __get_url(self, url, tenant=""):
        """
        Genera la URL completa del endpoint a partir del nombre de dominio,
        el puerto y la ruta.
        :param url: str, la ruta del endpoint
        :param tenant: str, el nombre del inquilino (opcional)
        :return: str, la URL completa del endpoint
        """
        if tenant:
            tenant += "."
        if PORT in ("80", "443"):
            puerto = ""
        else:
            puerto = f":{PORT}"

        return f"{PROTOCOLO}://{self.domain}{puerto}/{url}"

    def get(self, url, params=None, timeout=10, **kwargs):
        """
        Realiza una solicitud GET a la URL especificada.

        :param url: str, la ruta del endpoint
        :param params: dict, los parámetros de la solicitud (opcional)
        :param data: dict, los datos de la solicitud (opcional)
        :param json: dict, los datos de la solicitud en formato JSON (opcional)
        :param kwargs: dict, parámetros adicionales para la solicitud (opcional)
        :return: requests.Response, la respuesta de la solicitud GET
        :raises ValueError: si se produce un error en la solicitud
        """

        try:
            url = self.__get_url(url)
            logging.info("GET %s ", url)
            response = requests.get(
                url,
                headers=self.headers,
                params=params,
                timeout=timeout,
                **kwargs,
            )
        except requests.exceptions.HTTPError as http_error:
            error_msg = self.__handle_http_error(http_error)
            logging.error(http_error)
            raise ValueError(error_msg) from http_error
        except requests.exceptions.Timeout as timeout_error:
            logging.error("Timeout de la solicitud: %s", str(timeout_error))
            raise ValueError(
                f"Timeout de la solicitud: {str(timeout_error)}"
            ) from timeout_error
        except requests.exceptions.TooManyRedirects as redirects_error:
            logging.error(
                "Demasiados redireccionamientos: %s", str(redirects_error)
            )
            raise ValueError(
                f"Demasiados redireccionamientos: {str(redirects_error)}"
            ) from redirects_error
        except requests.exceptions.SSLError as ssl_error:
            logging.error("Error SSL: %s", str(ssl_error))
            raise ValueError(f"Error SSL: {str(ssl_error)}") from ssl_error
        except requests.exceptions.ProxyError as proxy_error:
            logging.error("Error del proxy: %s", str(proxy_error))
            raise ValueError(
                f"Error del proxy: {str(proxy_error)}"
            ) from proxy_error
        except requests.exceptions.ConnectionError as connection_error:
            logging.error("Error de conexión: %s", str(connection_error))
            raise ValueError(
                f"Error de conexión: {str(connection_error)}"
            ) from connection_error
        except requests.exceptions.RequestException as request_error:
            logging.error("Error de solicitud: %s", str(request_error))
            raise ValueError(
                f"Error de solicitud: {str(request_error)}"
            ) from request_error

        return response

    def post(
        self, url, params=None, data=None, json_data=None, timeout=10, **kwargs
    ):
        """
        Realiza una solicitud POST a la URL especificada.

        :param url: str, la ruta del endpoint
        :param params: dict, los parámetros de la solicitud (opcional)
        :param data: dict, los datos de la solicitud (opcional)
        :param json: dict, los datos de la solicitud en formato JSON (opcional)
        :param kwargs: dict, parámetros adicionales para la solicitud (opcional)
        :return: requests.Response, la respuesta de la solicitud POST
        :raises ValueError: si se produce un error en la solicitud
        """
        try:
            url = self.__get_url(url)
            logging.info("POST %s ", url)
            response = requests.post(
                url,
                headers=self.headers,
                data=data,
                json=json_data,
                params=params,
                timeout=timeout,
                **kwargs,
            )
            if response.status_code == 200:
                return response
            elif response.status_code == 201:
                return response
            elif response.status_code == 400:
                return response
            logging.info("POST %s", response.status_code)
            logging.info("POST %s", response.text)

            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            error_msg = self.__handle_http_error(response.status_code)
            logging.error(http_error)
            raise ValueError(error_msg) from http_error

        except requests.exceptions.Timeout as timeout_error:
            logging.error("Timeout de la solicitud: %s", str(timeout_error))
            raise ValueError(
                f"Timeout de la solicitud: {str(timeout_error)}"
            ) from timeout_error
        except requests.exceptions.TooManyRedirects as redirects_error:
            logging.error(
                "Demasiados redireccionamientos: %s", str(redirects_error)
            )
            raise ValueError(
                f"Demasiados redireccionamientos: {str(redirects_error)}"
            ) from redirects_error
        except requests.exceptions.SSLError as ssl_error:
            logging.error("Error SSL: %s", str(ssl_error))
            raise ValueError(f"Error SSL: {str(ssl_error)}") from ssl_error
        except requests.exceptions.ProxyError as proxy_error:
            logging.error("Error del proxy: %s", str(proxy_error))
            raise ValueError(
                f"Error del proxy: {str(proxy_error)}"
            ) from proxy_error
        except requests.exceptions.ConnectionError as connection_error:
            logging.error("Error de conexión: %s", str(connection_error))
            raise ValueError(
                f"Error de conexión: {str(connection_error)}"
            ) from connection_error
        except requests.exceptions.RequestException as request_error:
            logging.error("Error de solicitud: %s", str(request_error))
            raise ValueError(
                f"Error de solicitud: {str(request_error)}"
            ) from request_error
        return response

    def put(self, url, json_data=None, timeout=10, **kwargs):
        """
        Realiza una solicitud PUT a la URL especificada.

        :param url: str, la ruta del endpoint
        :param data: dict, los datos de la solicitud (opcional)
        :param json: dict, los datos de la solicitud en formato JSON (opcional)
        :param kwargs: dict, parámetros adicionales para la solicitud (opcional)
        :return: requests.Response, la respuesta de la solicitud PUT
        :raises HTTPError: si se produce un error HTTP no válido en la respuesta
        :raises RequestException: si se produce un error en la solicitud
        """
        try:
            url = self.__get_url(url)
            logging.info("PUT %s ", url)
            response = requests.put(
                url,
                headers=self.headers,
                json=json_data,
                timeout=timeout,
                **kwargs,
            )
            if response.status_code == 200:
                return response
            elif response.status_code == 400:
                return response
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            error_msg = self.__handle_http_error(response.status_code)
            logging.error(http_error)
            raise ValueError(error_msg) from http_error
        except requests.exceptions.Timeout as timeout_error:
            logging.error("Timeout de la solicitud: %s", str(timeout_error))
            raise ValueError(
                f"Timeout de la solicitud: {str(timeout_error)}"
            ) from timeout_error
        except requests.exceptions.TooManyRedirects as redirects_error:
            logging.error(
                "Demasiados redireccionamientos: %s", str(redirects_error)
            )
            raise ValueError(
                f"Demasiados redireccionamientos: {str(redirects_error)}"
            ) from redirects_error
        except requests.exceptions.SSLError as ssl_error:
            logging.error("Error SSL: %s", str(ssl_error))
            raise ValueError(f"Error SSL: {str(ssl_error)}") from ssl_error
        except requests.exceptions.ProxyError as proxy_error:
            logging.error("Error del proxy: %s", str(proxy_error))
            raise ValueError(
                f"Error del proxy: {str(proxy_error)}"
            ) from proxy_error
        except requests.exceptions.ConnectionError as connection_error:
            logging.error("Error de conexión: %s", str(connection_error))
            raise ValueError(
                f"Error de conexión: {str(connection_error)}"
            ) from connection_error
        except requests.exceptions.RequestException as request_error:
            logging.error("Error de solicitud: %s", str(request_error))
            raise ValueError(
                f"Error de solicitud: {str(request_error)}"
            ) from request_error
        return response

    def patch(self, url, params=None, data=None, json_data=None, **kwargs):
        """
        Realiza una solicitud PUT a la URL especificada.

        :param url: str, la ruta del endpoint
        :param data: dict, los datos de la solicitud (opcional)
        :param json: dict, los datos de la solicitud en formato JSON (opcional)
        :param kwargs: dict, parámetros adicionales para la solicitud (opcional)
        :return: requests.Response, la respuesta de la solicitud PUT
        :raises HTTPError: si se produce un error HTTP no válido en la respuesta
        :raises RequestException: si se produce un error en la solicitud
        """
        try:
            url = self.__get_url(url)
            logging.info("PATCH %s ", url)
            logging.info(type(json_data))
            response = self.session.request(
                "PATCH",
                url,
                headers=self.headers,
                data=data,
                json=json_data,
                params=params,
                **kwargs,
            )
            if response.status_code == 200:
                return response
            elif response.status_code == 400:
                return response
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            error_msg = self.__handle_http_error(response.status_code)
            logging.error(http_error)
            raise ValueError(error_msg) from http_error
        except requests.exceptions.Timeout as timeout_error:
            logging.error("Timeout de la solicitud: %s", str(timeout_error))
            raise ValueError(
                f"Timeout de la solicitud: {str(timeout_error)}"
            ) from timeout_error
        except requests.exceptions.TooManyRedirects as redirects_error:
            logging.error(
                "Demasiados redireccionamientos: %s", str(redirects_error)
            )
            raise ValueError(
                f"Demasiados redireccionamientos: {str(redirects_error)}"
            ) from redirects_error
        except requests.exceptions.SSLError as ssl_error:
            logging.error("Error SSL: %s", str(ssl_error))
            raise ValueError(f"Error SSL: {str(ssl_error)}") from ssl_error
        except requests.exceptions.ProxyError as proxy_error:
            logging.error("Error del proxy: %s", str(proxy_error))
            raise ValueError(
                f"Error del proxy: {str(proxy_error)}"
            ) from proxy_error
        except requests.exceptions.ConnectionError as connection_error:
            logging.error("Error de conexión: %s", str(connection_error))
            raise ValueError(
                f"Error de conexión: {str(connection_error)}"
            ) from connection_error
        except requests.exceptions.RequestException as request_error:
            logging.error("Error de solicitud: %s", str(request_error))
            raise ValueError(
                f"Error de solicitud: {str(request_error)}"
            ) from request_error
        return response

    def delete(self, url, **kwargs):
        """
        Realiza una solicitud DELETE a la URL especificada.

        :param url: str, la ruta del endpoint
        :return: requests.Response, la respuesta de la solicitud DELETE
        :raises ValueError: si se produce un error en la solicitud
        """
        try:
            url = self.__get_url(url)
            logging.info("DELETE %s ", url)
            response = self.session.request(
                "DELETE", url, headers=self.headers, **kwargs
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            error_msg = self.__handle_http_error(response.status_code)
            logging.error(http_error)
            raise ValueError(error_msg) from http_error
        except requests.exceptions.Timeout as timeout_error:
            logging.error("Timeout de la solicitud: %s", str(timeout_error))
            raise ValueError(
                f"Timeout de la solicitud: {str(timeout_error)}"
            ) from timeout_error
        except requests.exceptions.TooManyRedirects as redirects_error:
            logging.error(
                "Demasiados redireccionamientos: %s", str(redirects_error)
            )
            raise ValueError(
                f"Demasiados redireccionamientos: {str(redirects_error)}"
            ) from redirects_error
        except requests.exceptions.SSLError as ssl_error:
            logging.error("Error SSL: %s", str(ssl_error))
            raise ValueError(f"Error SSL: {str(ssl_error)}") from ssl_error
        except requests.exceptions.ProxyError as proxy_error:
            logging.error("Error del proxy: %s", str(proxy_error))
            raise ValueError(
                f"Error del proxy: {str(proxy_error)}"
            ) from proxy_error
        except requests.exceptions.ConnectionError as connection_error:
            logging.error("Error de conexión: %s", str(connection_error))
            raise ValueError(
                f"Error de conexión: {str(connection_error)}"
            ) from connection_error
        except requests.exceptions.RequestException as request_error:
            logging.error("Error de solicitud: %s", str(request_error))
            raise ValueError(
                f"Error de solicitud: {str(request_error)}"
            ) from request_error
        return response

    def __handle_http_error(self, status_code):
        """
        Maneja y devuelve un mensaje de error descriptivo para un código de estado HTTP dado.

        :param status_code: int, el código de estado HTTP que se debe manejar.
        :return: str, mensaje de error descriptivo correspondiente al código de estado.

        """

        if status_code == 400:
            return "Error 400: Solicitud incorrecta. Verifica los datos proporcionados."
        elif status_code == 401:
            return "Acceso denegado. Usuario o contraseña invalida!."
        elif status_code == 403:
            return (
                "Acceso denegado. No se te permite acceder a este contenido por,"
                "razones de seguridad o permisos."
            )
        elif status_code == 404:
            return "Error: Registro no encontrado. Verifica los datos proporcionado."
        elif status_code == 405:
            return (
                "Error 405. Solicitud realizada no está permitida "
                "para acceder al recurso solicitado."
            )
        elif status_code == 500:
            return "Error 500: Error interno del servidor."
        elif status_code == 502:
            return "Error 502: Puerta de enlace incorrecta."
        elif status_code == 503:
            return "Error 503: Servicio no disponible."
        elif status_code == 504:
            return (
                "Error 504: Tiempo de espera de la puerta de enlace agotado."
            )
        elif status_code == 429:
            return "Error 429: Demasiadas solicitudes. Inténtalo de nuevo más tarde."
        elif status_code == 408:
            return "Error 408: Tiempo de espera de la solicitud agotado."
        elif status_code == 503:
            return "Error 503: Servicio no disponible."
        else:
            return f"Error HTTP: {status_code}"
