from fastapi import FastAPI
from pydantic import BaseModel

from sentinel.sentim import send_request

app = FastAPI()


class CreateAnalysisRequest(BaseModel):
    text: str


@app.post("/analyze")
def create_analysis(create_analysis_request: CreateAnalysisRequest):
    sentiment = send_request(create_analysis_request.text)

    if sentiment == "positive":
        return {"sentiment": "positive"}
    else:
        return {"sentiment": "negative"}
