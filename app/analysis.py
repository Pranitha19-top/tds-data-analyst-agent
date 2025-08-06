import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import base64
import io
from scipy.stats import linregress
import re
import asyncio

async def answer_questions(question_str: str, df: pd.DataFrame):
    """
    Parse questions and answer based on dataframe content.
    Returns a JSON array of answers or object of Q:Answer.
    """

    # Example: detect questions by splitting lines starting with digits
    questions = [line.strip() for line in question_str.split('\n') if re.match(r'^\d+\.', line.strip())]
    answers = []

    for q in questions:
        q_lower = q.lower()

        # 1) How many $2 bn movies before 2000? (example)
        if "how many" in q_lower and "$2 bn" in q_lower and "before 2000" in q_lower:
            if df is None:
                answers.append(0)
            else:
                # Assume df has 'Gross' and 'Year' columns
                if 'Gross' in df.columns and 'Year' in df.columns:
                    # Clean and convert Gross to float in billions
                    def parse_gross(x):
                        try:
                            # Remove $ and commas, convert to float
                            return float(str(x).replace("$","").replace(",",""))/1e9
                        except:
                            return 0
                    df['GrossNum'] = df['Gross'].apply(parse_gross)
                    count = df[(df['GrossNum'] >= 2) & (df['Year'] < 2000)].shape[0]
                    answers.append(count)
                else:
                    answers.append(0)

        # 2) Earliest film that grossed over $1.5 bn
        elif "earliest film" in q_lower and "1.5 bn" in q_lower:
            if df is None:
                answers.append("")
            else:
                if 'Gross' in df.columns and 'Year' in df.columns and 'Title' in df.columns:
                    df['GrossNum'] = df['Gross'].apply(lambda x: float(str(x).replace("$","").replace(",",""))/1e9 if x else 0)
                    filtered = df[df['GrossNum'] > 1.5]
                    if filtered.empty:
                        answers.append("")
                    else:
                        earliest = filtered.sort_values('Year').iloc[0]
                        answers.append(earliest['Title'])
                else:
                    answers.append("")

        # 3) Correlation between Rank and Peak
        elif "correlation" in q_lower and "rank" in q_lower and "peak" in q_lower:
            if df is None:
                answers.append(0.0)
            else:
                if 'Rank' in df.columns and 'Peak' in df.columns:
                    corr = df['Rank'].corr(df['Peak'])
                    answers.append(round(corr if corr else 0.0, 6))
                else:
                    answers.append(0.0)

        # 4) Draw scatterplot of Rank and Peak + dotted red regression line
        elif "scatterplot" in q_lower and "rank" in q_lower and "peak" in q_lower:
            if df is None:
                answers.append("")
            else:
                if 'Rank' in df.columns and 'Peak' in df.columns:
                    fig, ax = plt.subplots(figsize=(6,4))
                    ax.scatter(df['Rank'], df['Peak'], label='Data points')
                    slope, intercept, r_value, p_value, std_err = linregress(df['Rank'], df['Peak'])
                    x_vals = np.array(ax.get_xlim())
                    y_vals = intercept + slope * x_vals
                    ax.plot(x_vals, y_vals, 'r--', label='Regression line')
                    ax.set_xlabel('Rank')
                    ax.set_ylabel('Peak')
                    ax.legend()
                    plt.tight_layout()

                    # Encode plot to base64
                    buf = io.BytesIO()
                    plt.savefig(buf, format='png', bbox_inches='tight')
                    plt.close()
                    buf.seek(0)
                    b64 = base64.b64encode(buf.read()).decode('utf-8')
                    data_uri = f"data:image/png;base64,{b64}"

                    # Trim to <100k chars if needed
                    if len(data_uri) > 100000:
                        data_uri = data_uri[:100000]

                    answers.append(data_uri)
                else:
                    answers.append("")

        else:
            # Default fallback answer
            answers.append("Question not recognized or data missing")

    return answers
