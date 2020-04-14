from zoomus import ZoomClient
import secrets
import requests


def generic_zoom_request(request="report/daily", params=None):
    """Perform an unlisted request on zoom"""

    # noinspection PyUnresolvedReferences,PyUnresolvedReferences
    client = ZoomClient(secrets.API_KEY, secrets.API_SECRET)
    if params is None:
        params = {}
    headers = {"Authorization": "Bearer {}".format(client.config.get("token"))}

    result = requests.get('https://api.zoom.us/v2/' + request, params, headers=headers)
    return result
