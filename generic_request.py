# noinspection PyPackageRequirements
from zoomus import ZoomClient
import secrets
# noinspection PyPackageRequirements
import requests


def generic_zoom_request(request="report/daily", params=None, request_type='get'):
    """Perform an unlisted request on zoom"""

    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    client = ZoomClient(secrets.API_KEY, secrets.API_SECRET)
    if params is None:
        params = {}
    headers = {
        "Authorization": "Bearer {}".format(client.config.get("token")),
        'content-type': "application/json"
    }
    result = None
    if request_type == 'get':
        result = requests.get('https://api.zoom.us/v2/' + request, params, headers=headers)
    elif request_type == 'patch':
        result = requests.patch('https://api.zoom.us/v2/' + request, data=params, headers=headers)
    elif request_type == 'post':
        result = requests.post('https://api.zoom.us/v2/' + request, data=params, headers=headers)
    return result
