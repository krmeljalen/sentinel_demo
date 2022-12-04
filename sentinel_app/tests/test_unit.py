from unittest.mock import Mock, patch

import pytest

from sentinel.api import CreateAnalysisRequest, create_analysis


@pytest.mark.parametrize(
    ["response", "expected_sentiment"],
    [
        (
            {
                "result": {"polarity": -0.18, "type": "negative"},
                "sentences": [
                    {
                        "sentence": "This is a test.",
                        "sentiment": {"polarity": -0.18, "type": "negative"},
                    },
                ],
            },
            "negative",
        ),
        (
            {
                "result": {"polarity": 0.18, "type": "positive"},
                "sentences": [
                    {
                        "sentence": "This is a test.",
                        "sentiment": {"polarity": 0.18, "type": "positive"},
                    },
                ],
            },
            "positive",
        ),
    ],
)
@patch("sentinel.sentim.requests.post")
def test_create_analysis_where_api_succeeds(mock_post, response, expected_sentiment):
    mock_json = Mock(return_value=response)
    mock_post.return_value = Mock(json=mock_json, status_code=200)

    response = create_analysis(CreateAnalysisRequest(text="This is a test."))

    assert response == {"sentiment": expected_sentiment}
    assert mock_post.called_with(
        "https://sentim-api.herokuapp.com/api/v1/",
        json={"text": "This is a test."},
        timeout=3,
    )


@patch("sentinel.sentim.requests.post")
def test_create_analysis_where_api_returns_unexpected_body(mock_post):
    mock_json = Mock(return_value={"unexpected": "json"})
    mock_post.return_value = Mock(json=mock_json, status_code=200)

    response = create_analysis(CreateAnalysisRequest(text="This is a test."))

    assert response == {"sentiment": "negative"}
    assert mock_post.called_with(
        "https://sentim-api.herokuapp.com/api/v1/",
        json={"text": "This is a test."},
        timeout=3,
    )


@patch("sentinel.sentim.requests.post")
def test_create_analysis_where_api_fails(mock_post):
    mock_post.return_value = Mock(status_code=500)

    response = create_analysis(CreateAnalysisRequest(text="This is a test."))

    assert response == {"sentiment": "negative"}
    assert mock_post.called_with(
        "https://sentim-api.herokuapp.com/api/v1/",
        json={"text": "This is a test."},
        timeout=3,
    )
