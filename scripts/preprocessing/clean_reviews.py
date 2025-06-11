
import pandas as pd
import emoji
import re
from scripts.utils.helpers import clean_text
def clean_reviews(df:pd.DataFrame)->pd.DataFrame:
    # Remove Duplicates
    df=df.drop_duplicates(subset=["review", "date", "bank"], keep="first")
    
    #def convert_emoji(x):
       # return emoji.demojize(x)
    # Apply cleaning function from helper
    df["review"]= df["review"].apply(clean_text)
    return df
