from flask import Flask, render_template, request, jsonify
import nltk
from bs4 import BeautifulSoup
import spacy
import re
from collections import Counter

app = Flask(__name__)

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Load spaCy model
nlp = spacy.load('en_core_web_sm')

def analyze_content(content):
    # Parse HTML content
    soup = BeautifulSoup(content, 'html.parser')
    
    # Initialize scores
    scores = {
        'llm_understanding': 0,
        'structure': 0,
        'link_references': 0
    }
    
    # Analyze LLM Understanding
    text = soup.get_text()
    doc = nlp(text)
    
    # Check for clear language and sentence structure
    sentences = list(doc.sents)
    avg_sentence_length = sum(len(sent) for sent in sentences) / len(sentences)
    if 10 <= avg_sentence_length <= 20:
        scores['llm_understanding'] += 20
    
    # Check for headings
    headings = soup.find_all(['h1', 'h2', 'h3'])
    if len(headings) >= 3:
        scores['llm_understanding'] += 15
    
    # Check for lists
    lists = soup.find_all(['ul', 'ol'])
    if len(lists) > 0:
        scores['llm_understanding'] += 15
    
    # Check for formatting
    if soup.find('strong') or soup.find('em'):
        scores['llm_understanding'] += 10
    
    # Analyze Structure
    # Check for TL;DR or key takeaways
    if re.search(r'TL;DR|Key Takeaways|Summary', text, re.IGNORECASE):
        scores['structure'] += 20
    
    # Check for Q&A format
    questions = re.findall(r'\?', text)
    if len(questions) >= 3:
        scores['structure'] += 15
    
    # Check for schema-like content
    if re.search(r'FAQ|How to|Guide|Tutorial', text, re.IGNORECASE):
        scores['structure'] += 15
    
    # Analyze Link References
    # Check for external links
    links = soup.find_all('a')
    if len(links) >= 3:
        scores['link_references'] += 20
    
    # Check for citations or references
    if re.search(r'Source|Reference|Cited|According to', text, re.IGNORECASE):
        scores['link_references'] += 15
    
    # Check for evergreen content indicators
    evergreen_terms = ['guide', 'tutorial', 'how to', 'best practices', 'fundamentals']
    if any(term in text.lower() for term in evergreen_terms):
        scores['link_references'] += 15
    
    # Calculate total score
    total_score = sum(scores.values())
    
    # Generate recommendations
    recommendations = []
    if scores['llm_understanding'] < 40:
        recommendations.append("Improve content structure with more headings and lists")
    if scores['structure'] < 40:
        recommendations.append("Add a TL;DR section and more Q&A format content")
    if scores['link_references'] < 40:
        recommendations.append("Include more external links and citations")
    
    return {
        'total_score': total_score,
        'category_scores': scores,
        'recommendations': recommendations
    }

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    content = request.json.get('content', '')
    if not content:
        return jsonify({'error': 'No content provided'}), 400
    
    analysis = analyze_content(content)
    return jsonify(analysis)

if __name__ == '__main__':
    app.run(debug=True) 