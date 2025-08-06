import io
import base64
import pandas as pd
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app import analysis, scraping, utils

app = FastAPI(title="Data Analyst Agent API")

@app.post("/api/")
async def analyze_data(
    questions: UploadFile = File(...),
    files: list[UploadFile] = File(default=None)
):
    # Read questions.txt
    question_text = await questions.read()
    question_str = question_text.decode("utf-8")

    # Load CSV files (if any) into dict of dataframes
    dataframes = {}
    if files:
        for file in files:
            content = await file.read()
            filename = file.filename
            if filename.endswith(".csv"):
                df = pd.read_csv(io.BytesIO(content))
                dataframes[filename] = df

    # Parse questions & extract URLs if any
    urls = utils.extract_urls(question_str)

    # If Wikipedia URL found, scrape data table
    wiki_df = None
    if urls:
        for url in urls:
            if "wikipedia.org" in url:
                wiki_df = await scraping.scrape_wikipedia_table(url)
                break

    # Combine available data sources
    df_to_use = None
    if wiki_df is not None:
        df_to_use = wiki_df
    elif dataframes:
        # Use the first csv for demo
        df_to_use = list(dataframes.values())[0]

    # Analyze & answer questions
    answers = await analysis.answer_questions(question_str, df_to_use)

    return JSONResponse(content=answers)
