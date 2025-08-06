import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import requests
from bs4 import BeautifulSoup

def extract_urls(text: str):
    """
    Extract all URLs from a given text string
    """
    url_pattern = r'https?://[^\s]+'
    urls = re.findall(url_pattern, text)
    return urls


def scrape_wikipedia_table(url: str):
    """
    Scrapes the first table from a Wikipedia page and returns it as a cleaned DataFrame
    """
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "wikitable"})

    df = pd.read_html(str(table))[0]

    # Try to normalize column names (depends on Wikipedia table)
    df.columns = [str(c).strip() for c in df.columns]
    if "Title" not in df.columns and "Film" in df.columns:
        df = df.rename(columns={"Film": "Title"})

    # Clean gross and year if present
    if "Worldwide gross" in df.columns:
        df["Worldwide gross"] = (
            df["Worldwide gross"]
            .astype(str)
            .str.replace(r"[^0-9.]", "", regex=True)
            .astype(float)
        )

    if "Year" in df.columns:
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

    if "Peak" in df.columns:
        df["Peak"] = pd.to_numeric(df["Peak"], errors="coerce")

    if "Rank" in df.columns:
        df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")

    return df


def plot_rank_vs_peak(df):
    """
    Creates scatterplot of Rank vs Peak with dotted red regression line, returns base64 PNG string
    """
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df, x="Rank", y="Peak")
    sns.regplot(data=df, x="Rank", y="Peak", scatter=False, color="red", linestyle='dotted')

    plt.xlabel("Rank")
    plt.ylabel("Peak")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)

    base64_image = base64.b64encode(buf.read()).decode("utf-8")
    return f"data:image/png;base64,{base64_image}"


def handle_question_request(req):
    """
    Main entry point to handle incoming request from app.py
    - Reads the question file
    - Handles optional attached files
    - Returns a 4-element response
    """
    # 1. Read the question text
    question_file = req.files.get("questions.txt")
    question_text = question_file.read().decode("utf-8")

    # 2. Extract URLs
    urls = extract_urls(question_text)

    if urls:
        # Handle Wikipedia scraping (sample use case)
        url = urls[0]
        df = scrape_wikipedia_table(url)

        # Example answers
        # Q1: How many $2bn movies before 2000?
        q1 = df[(df["Worldwide gross"] > 2_000_000_000) & (df["Year"] < 2000)].shape[0]

        # Q2: Earliest film > $1.5bn
        df_high = df[df["Worldwide gross"] > 1_500_000_000]
        earliest_film = df_high.sort_values("Year").iloc[0]["Title"]

        # Q3: Correlation between Rank and Peak
        correlation = df["Rank"].corr(df["Peak"])
        correlation = round(correlation, 6)

        # Q4: Scatterplot
        img_uri = plot_rank_vs_peak(df)

        return [q1, earliest_film, correlation, img_uri]

    # Handle more cases here (e.g., if CSV is uploaded)
    return ["No URL found", "", 0.0, ""]
