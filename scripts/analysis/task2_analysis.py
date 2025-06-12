import os
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import spacy
import textacy
from textacy import extract
from collections import defaultdict
from tabulate import tabulate

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm', disable=['ner', 'parser'])
except Exception as e:
    print(f"spaCy model load error: {e}")
    print("Try running: python -m spacy download en_core_web_sm")
    exit()

# Paths
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
cleaned_data_path = os.path.join(project_root, 'data', 'cleaned')
output_path = os.path.join(project_root, 'data', 'analysis')
os.makedirs(output_path, exist_ok=True)

# Filenames
bank_files = {
    'bank_of_abyssinia': 'cleaned_bank_of_abyssinia_20250612_145335.csv',
    'commercial_bank_of_ethiopia': 'cleaned_commercial_bank_of_ethiopia_20250612_145335.csv',
    'dashen_bank': 'cleaned_dashen_bank_20250612_145335.csv'
}

# Sentiment analysis
def get_sentiment_scores(reviews):
    analyzer = SentimentIntensityAnalyzer()
    sentiments, scores = [], []
    for review in reviews:
        try:
            vs = analyzer.polarity_scores(review)
            score = vs['compound']
            label = 'POSITIVE' if score >= 0.05 else 'NEGATIVE' if score <= -0.05 else 'NEUTRAL'
            sentiments.append(label)
            scores.append(score)
        except:
            sentiments.append('NEUTRAL')
            scores.append(0.0)
    return sentiments, scores

# Keyword extraction
def extract_keywords(review):
    try:
        doc = nlp(review)
        noun_phrases = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text.split()) <= 3]
        doc2 = textacy.make_spacy_doc(review, lang='en_core_web_sm')
        ngrams = [ngram.lower() for ngram in extract.ngrams(doc2, n=[2, 3], filter_stops=True, filter_punct=True)]
        return list(set(noun_phrases + ngrams))
    except:
        return []

# Theme assignment rules
theme_rules = {
    'bank_of_abyssinia': {
        'Account Access': ['login error', 'access issue', 'password', 'authentication'],
        'Transactions': ['payment issue', 'transfer', 'delay', 'transaction'],
        'UI/UX': ['interface', 'app crash', 'design', 'navigation'],
        'Support': ['support', 'customer service', 'response'],
        'Feature Requests': ['new feature', 'missing option', 'update app']
    },
    'commercial_bank_of_ethiopia': {
        'Account Access': ['login failed', 'authentication error', 'sign in'],
        'Transactions': ['transfer delay', 'payment slow', 'transaction failed'],
        'UI/UX': ['app slow', 'layout', 'crash'],
        'Support': ['customer care', 'service delay', 'support unhelpful'],
        'Feature Requests': ['add feature', 'new option']
    },
    'dashen_bank': {
        'Account Access': ['login', 'sign in', 'access problem'],
        'Transactions': ['transfer failed', 'payment delay', 'transaction issue'],
        'UI/UX': ['app freeze', 'interface issue', 'ui problem'],
        'Support': ['support delay', 'unresponsive support'],
        'Feature Requests': ['feature request', 'missing feature']
    }
}

# Theme assignment
def assign_themes(keywords, bank_key):
    themes = []
    for kw in keywords:
        for theme, rule_keywords in theme_rules.get(bank_key, {}).items():
            if any(rk in kw for rk in rule_keywords):
                themes.append(theme)
                break
    return list(set(themes)) or ['Other']

# Main pipeline
def process_reviews():
    all_results = []
    for bank_key, filename in bank_files.items():
        filepath = os.path.join(cleaned_data_path, filename)
        if not os.path.exists(filepath):
            print(f"File not found: {filepath}")
            continue

        print(f"\nProcessing: {filename}")
        df = pd.read_csv(filepath)
        df['bank'] = bank_key.replace('_', ' ').title()

        # Columns check
        if not {'review', 'rating', 'date', 'source'}.issubset(df.columns):
            print(f"Missing columns in {filename}")
            continue

        # VADER sentiment
        df['sentiment_label'], df['sentiment_score'] = get_sentiment_scores(df['review'])

        # Keywords & themes
        df['keywords'] = df['review'].apply(extract_keywords)
        df['themes'] = df['keywords'].apply(lambda kws: assign_themes(kws, bank_key))

        # Save individual file
        out_file = os.path.join(output_path, f'analysis_{bank_key}_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv')
        df.to_csv(out_file, index=False)
        print(f"Saved: {out_file}")

        all_results.append(df)

        # Print aggregation
        sentiment_summary = df.groupby(['rating', 'sentiment_label'])['sentiment_score'].agg(['mean', 'count']).reset_index()
        print(tabulate(sentiment_summary, headers='keys', tablefmt='psql'))

    return pd.concat(all_results, ignore_index=True) if all_results else None

if __name__ == "__main__":
    process_reviews()
