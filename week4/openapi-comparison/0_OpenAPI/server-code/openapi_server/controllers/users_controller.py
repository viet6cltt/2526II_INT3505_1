import connexion
from typing import Dict
from typing import Tuple
from typing import Union

from openapi_server import util


def users_get(debug=None, theme=None):  # noqa: E501
    """Get users with debug mode

     # noqa: E501

    :param debug: Enable debug mode
    :type debug: int
    :param theme: UI theme preference
    :type theme: str

    :rtype: Union[None, Tuple[None, int], Tuple[None, int, Dict[str, str]]
    """
    return 'do some magic!'
