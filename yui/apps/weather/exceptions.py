from aiohttp.client_exceptions import ClientConnectorCertificateError
from aiohttp.client_exceptions import ClientPayloadError


class WeatherResponseError(Exception):
    pass


class WeatherRequestError(Exception):
    pass


EXCEPTIONS = (
    ClientPayloadError,  # Bad HTTP Response
    ValueError,  # JSON Error
    ClientConnectorCertificateError,  # TLS expired
    WeatherResponseError,  # Bad HTTP Response
)
