from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()
text = "This app is amazing! Super fast and user-friendly."
score = analyzer.polarity_scores(text)
print(f"Sentiment scores for '{text}':")
print(score)
