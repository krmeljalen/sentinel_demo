import requests


def send_request(text: str) -> str:
    response = requests.post(
        "https://sentim-api.herokuapp.com/api/v1/",
        json={"text": text},
        timeout=3,
    )

    if response.status_code != 200:
        return "negative"

    try:
        return response.json()["result"]["type"]
    except:
        return "negative"
