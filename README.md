# AI SEO Content Analyzer

A tool that analyzes blog content for AI SEO optimization, providing scores and recommendations for improving content for AI and search engine visibility.

## Features

- Analyzes content for LLM understanding
- Evaluates content structure and formatting
- Checks for proper link references and citations
- Provides an overall score and specific recommendations
- Modern, responsive web interface

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and navigate to `http://localhost:5000`

## Usage

1. Paste your blog content into the text area
2. Click "Analyze Content"
3. Review your scores and recommendations
4. Make improvements based on the suggestions

## Scoring Categories

- **LLM Understanding**: Evaluates content clarity, structure, and formatting
- **Content Structure**: Checks for proper organization, TL;DR sections, and Q&A formats
- **Link References**: Analyzes external links, citations, and evergreen content indicators

## Technologies Used

- Flask
- NLTK
- spaCy
- BeautifulSoup4
- TailwindCSS 