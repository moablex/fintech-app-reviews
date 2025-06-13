import pandas as pd
import psycopg2
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import os

# Connect to PostgreSQL
db_params = {
    'dbname': 'bank_reviews',
    'user': 'postgres',
    'password': 'newpassword',
    'host': 'localhost',
    'port': '5432'
}

conn = psycopg2.connect(**db_params)
df = pd.read_sql("""
    SELECT r.*, b.name as bank_name
    FROM reviews r
    JOIN banks b ON r.bank_id = b.id
""", conn)
conn.close()

# Output folder
os.makedirs("outputs", exist_ok=True)

### VISUALIZATION SECTION ###

# Plot 1: Sentiment Distribution by Bank
plt.figure(figsize=(10, 6))
sns.countplot(data=df, x='bank_name', hue='sentiment_label', palette='Set2')
plt.title('Sentiment Distribution by Bank')
plt.xlabel('Bank')
plt.ylabel('Number of Reviews')
plt.xticks(rotation=45)
plt.legend(title='Sentiment')
plt.tight_layout()
plt.savefig("outputs/plot1_sentiment_by_bank.png")
plt.close()

# Plot 2: Rating Distribution by Bank
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x='bank_name', y='rating', palette='Set3')
plt.title('Rating Distribution by Bank')
plt.xlabel('Bank')
plt.ylabel('User Rating (1–5)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig("outputs/plot2_rating_distribution.png")
plt.close()

# Plot 3: WordClouds of Keywords per Bank
for bank in df['bank_name'].unique():
    keywords = ' '.join(df[df['bank_name'] == bank]['keywords'].dropna().astype(str))
    if keywords.strip():
        wc = WordCloud(width=800, height=400, background_color='white').generate(keywords)
        plt.figure(figsize=(10, 5))
        plt.imshow(wc, interpolation='bilinear')
        plt.axis('off')
        plt.title(f"Keyword Cloud - {bank}")
        plt.tight_layout()
        filename = f"outputs/plot3_keyword_cloud_{bank.lower().replace(' ', '_')}.png"
        plt.savefig(filename)
        plt.close()

# Plot 4: Top 10 Themes Across All Reviews
theme_counts = df['themes'].value_counts().head(10)
plt.figure(figsize=(10, 6))
sns.barplot(x=theme_counts.values, y=theme_counts.index, palette='coolwarm')
plt.title("Top 10 Frequent Themes in Reviews")
plt.xlabel("Number of Mentions")
plt.ylabel("Theme")
plt.tight_layout()
plt.savefig("outputs/plot4_top_themes.png")
plt.close()

# Plot 5: Average Rating vs. Sentiment Polarity
avg_sentiment = df.groupby('bank_name')['sentiment_score'].mean()
avg_rating = df.groupby('bank_name')['rating'].mean()
summary_df = pd.DataFrame({'avg_sentiment': avg_sentiment, 'avg_rating': avg_rating})

plt.figure(figsize=(8, 6))
sns.scatterplot(data=summary_df, x='avg_sentiment', y='avg_rating', hue=summary_df.index, s=100, palette='tab10')
plt.title("Avg Sentiment Score vs Avg User Rating")
plt.xlabel("Average Sentiment Polarity")
plt.ylabel("Average Rating")
for i in summary_df.index:
    plt.text(summary_df.loc[i, 'avg_sentiment'] + 0.01, summary_df.loc[i, 'avg_rating'] + 0.01, i, fontsize=9)
plt.tight_layout()
plt.savefig("outputs/plot5_sentiment_vs_rating.png")
plt.close()

### INSIGHTS SECTION ###

# Sentiment Breakdown per Bank
sentiment_summary = df.groupby(['bank_name', 'sentiment_label'])['review'].count().unstack().fillna(0)

# Identify 1+ Driver and Pain Point per Bank using keywords/themes
insights = {}
for bank in df['bank_name'].unique():
    bank_reviews = df[df['bank_name'] == bank]
    themes = bank_reviews['themes'].dropna().value_counts()
    keywords = ' '.join(bank_reviews['keywords'].dropna().astype(str))
    
    driver = themes[themes.index.str.contains('easy|fast|secure|helpful', case=False)].head(1)
    pain = themes[themes.index.str.contains('crash|error|support|login|slow', case=False)].head(1)
    
    insights[bank] = {
        'driver': driver.index[0] if not driver.empty else 'N/A',
        'pain_point': pain.index[0] if not pain.empty else 'N/A'
    }

# Save insights summary
with open("outputs/insights_summary.txt", "w") as f:
    f.write("Sentiment counts by bank:\n")
    f.write(sentiment_summary.to_string())
    f.write("\n\nIdentified drivers and pain points per bank:\n")
    for bank, vals in insights.items():
        f.write(f"\n{bank}:\n  Driver: {vals['driver']}\n  Pain Point: {vals['pain_point']}")
    f.write("\n\nTop 10 themes across all banks:\n")
    f.write(theme_counts.to_string())
    f.write("\n\nEthical Note: Users who leave reviews are more likely to have had strong negative experiences. These insights may not reflect the average user base.\n")

print("✅ Task 4 visualizations and insights saved to outputs/")
