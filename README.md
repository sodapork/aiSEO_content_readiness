# AI SEO Content Analyzer

A tool that analyzes blog content for AI SEO optimization, providing scores and recommendations for improving content for AI and search engine visibility.

## Features

- **Content Analysis**: Analyzes pasted content for LLM understanding, structure, and optimization
- **URL Fetching**: Fetch and analyze content directly from any website URL
- **Intent Analysis**: Determines search intent (informational, navigational, transactional, commercial)
- **Smart Content Extraction**: Automatically extracts main content from web pages
- **Comprehensive Scoring**: Evaluates multiple aspects of content quality
- **Modern Interface**: Responsive web interface with real-time analysis

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

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`

## Usage

### Method 1: Paste Content
1. Switch to the "Paste Content" tab
2. Paste your blog content into the text area
3. Click "Analyze Content"
4. Review your scores and recommendations

### Method 2: URL Analysis
1. Switch to the "Enter URL" tab
2. Enter a website URL (e.g., https://example.com/blog/post)
3. Click "Fetch" to extract content from the URL
4. The content will be automatically loaded into the text area
5. Click "Analyze Content" to get your analysis

## Scoring Categories

- **LLM Understanding**: Evaluates content clarity, structure, and formatting
- **Content Structure**: Checks for proper organization, TL;DR sections, and Q&A formats
- **Link References**: Analyzes external links, citations, and evergreen content indicators

## Intent Analysis

The tool analyzes your content to determine the primary search intent:

- **Informational**: Users seeking information, education, or answers
- **Navigational**: Users looking for a specific website or brand
- **Transactional**: Users ready to make a purchase or take action
- **Commercial**: Users researching products/services before deciding

## URL Feature

The URL fetching feature allows you to analyze content directly from any website:

- **Smart Content Extraction**: Automatically identifies and extracts main content
- **Metadata Extraction**: Captures page title and description
- **Error Handling**: Provides clear error messages for failed requests
- **Word Count**: Shows the number of words extracted
- **Multiple Formats**: Works with various website structures and content types

## Testing

Run the test script to verify the URL feature is working:

```bash
python test_url_feature.py
```

## Technologies Used

- **Backend**: Flask, NLTK, BeautifulSoup4, Requests
- **Frontend**: HTML, JavaScript, TailwindCSS
- **Content Processing**: LXML, Regular Expressions
- **HTTP Requests**: Requests library with proper headers and timeouts 