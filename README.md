# Fintech App Reviews Analysis

## Project Overview

This project analyzes customer reviews of Ethiopian banking apps from the Google Play Store to identify satisfaction drivers and pain points. The analysis includes:

- Scraping user reviews
- Sentiment analysis
- Thematic extraction of key topics
- Visualization of insights
- Storage in Oracle database

## Project Structure

```plaintext
fintech-app-reviews/
├── .github/                      # GitHub automation
│   ├── workflows/
│   │   └── ci.yml                # CI/CD pipeline
│   └── ISSUE_TEMPLATE/           # Issue templates
│       ├── bug_report.md
│       ├── feature_request.md
│       └── config.yml
├── data/                         # Datasets
│   ├── raw/                      # Raw scraped data
│   ├── cleaned/                  # Processed data
│   └── processed/                # Analysis outputs
├── notebooks/                    # Exploratory analysis
├── reports/                      # Final outputs
│   └── visuals/                  # Charts and graphs
├── scripts/                      # Processing pipeline
│   ├── scraping/                 # Review collection
│   ├── preprocessing/            # Data cleaning
│   ├── analysis/                 # NLP analysis
│   ├── database/                 # Database operations
│   └── utils/                    # Helper functions
├── tests/                        # Unit tests
├── .gitignore                    # Ignore files
├── environment.yml               # Conda environment
└── README.md                     # This file
```

## Environment Setup

1. Clone Repository

```bash
git clone https://github.com/moablex/fintech-app-reviews.git
cd fintech-app-reviews
```

2. Create Conda Environment

```bash
conda env create -f environment.yml
```

3. Activate Environment

```bash
conda activate myenv
```

4. Verify Installation

```bash
conda list
# Key packages should include:
# pandas, transformers, google-play-scraper, oracledb ..
```

## Continuous Integration

The GitHub Actions workflow (.github/workflows/ci.yml) automatically:

- Sets up Conda environment on push to main or setup-task branches

- Verifies environment creation

- Lists installed packages

## Troubleshooting

Common Issues:

    Conda environment creation fails:

```bash
    conda update -n base conda
    conda env update -f environment.yml
```

## Contribution

    Create feature branch: git checkout -b feature/your-feature

    Commit changes: git commit -m "Descriptive message"

    Push to remote: git push origin feature/your-feature

    Open pull request against main branch
