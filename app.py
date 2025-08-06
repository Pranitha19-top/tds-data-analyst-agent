from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import pandas as pd
import io

app = FastAPI()

@app.post("/analyze")
async def analyze(file: UploadFile = File(...), query: str = Form(...)):
    try:
        contents = await file.read()
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))

        # Very basic interpretation of query
        query_lower = query.lower()
        if "mean" in query_lower or "average" in query_lower:
            return df.mean(numeric_only=True).to_dict()
        elif "describe" in query_lower or "summary" in query_lower:
            return df.describe().to_dict()
        elif "columns" in query_lower:
            return {"columns": df.columns.tolist()}
        else:
            return {"message": "Sorry, I didn’t understand the query. Try asking for mean, summary, or column names."}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
