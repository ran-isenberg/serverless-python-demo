import json

import requests


def test_bad_request_invalid_body(api_url):
    body_str = json.dumps({'price': 5})
    response = requests.put(url=api_url, data=body_str)
    assert response.status_code == 400
