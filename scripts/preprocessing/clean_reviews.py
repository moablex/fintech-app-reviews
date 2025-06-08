
import pandas as pd
import emoji
import re
def clean_reviews(df:pd.DataFrame)->pd.DataFrame:
    # Remove Duplicates
    df=df.drop_duplicates(subset=["review", "date", "bank"], keep="first")
    
    #def convert_emoji(x):
       # return emoji.demojize(x)

    # Convert emojis in the 'review' column to text
    df["review"] = df["review"].apply(lambda x: emoji.demojize(x, language='en')  if pd.notnull(x) else "")
     #Remove URLs
    df["review"] = df["review"].apply(lambda x: re.sub(r'http\S+|www\S+|https\S+', '', x, flags=re.MULTILINE))
    # Step 3: Remove special characters and numbers (but keep .,!? for sentiment)
    df["review"] = df["review"].apply(lambda x: re.sub(r'[^a-zA-Z\s.,!?]', '', x))

    # Convert to lowercase
    df["review"] = df["review"].apply(lambda x: x.lower())

    # Remove extra whitespace
    df["review"] = df["review"].apply(lambda x: re.sub(r'\s+', ' ', x).strip())