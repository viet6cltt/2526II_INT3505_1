import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server.models.auth_refresh_post200_response import AuthRefreshPost200Response  # noqa: E501
from openapi_server import util


def auth_refresh_post():  # noqa: E501
    """Refresh access token

    Create new accesstoken from refresh token # noqa: E501


    :rtype: Union[AuthRefreshPost200Response, Tuple[AuthRefreshPost200Response, int], Tuple[AuthRefreshPost200Response, int, Dict[str, str]]
    """
    return 'do some magic!'
