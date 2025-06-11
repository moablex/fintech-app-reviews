import pandas as pd
import emoji
import re

def clean_text(text):
    if pd.isnull(text):
        return ""
    text = str(text)
    text = emoji.demojize(text, language='en')
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'[^a-zA-Z\s.,!?]', '', text)
    text = text.lower()
    text = re.sub(r'\s+', ' ', text).strip()
    return text