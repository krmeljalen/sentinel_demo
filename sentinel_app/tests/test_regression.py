import os

import pytest
import requests


@pytest.mark.parametrize(
    ["text", "expected_sentiment"],
    [
        ("I'm excited to get started.", "positive"),
        ("I'm nervous to get started.", "negative"),
        ("I'm anxious to get started.", "negative"),
    ],
)
def test_create_analysis(text, expected_sentiment):
    response = requests.post(
        f"{os.environ.get('BASE_URL', 'http://localhost:8000')}/analyze",
        json={"text": text},
    )

    assert response.status_code == 200
    assert response.json()["sentiment"] == expected_sentiment
