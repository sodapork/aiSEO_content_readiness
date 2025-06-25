from flask import Flask, render_template, request, jsonify
import nltk
from bs4 import BeautifulSoup
import re
from collections import Counter
import os
import requests
from urllib.parse import urlparse
import time
import json

app = Flask(__name__)

# Ensure NLTK data path includes user directory
nltk_data_dir = os.path.expanduser('~/nltk_data')
if nltk_data_dir not in nltk.data.path:
    nltk.data.path.append(nltk_data_dir)

print('NLTK data paths:', nltk.data.path)

# Download required NLTK data
try:
    nltk.download('punkt', download_dir=nltk_data_dir)
    nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_dir)
    nltk.download('tokenizers/punkt', download_dir=nltk_data_dir)
except Exception as e:
    print('NLTK download error:', e)
    nltk.download('all', download_dir=nltk_data_dir)

def simple_sent_tokenize(text):
    # Split on period, exclamation, or question mark followed by space or end of string
    return [s.strip() for s in re.split(r'[.!?](?:\s|$)', text) if s.strip()]

def analyze_keyword_intent(text):
    """
    Analyze content to determine the primary search intent and provide recommendations.
    Returns intent classification and specific optimization suggestions.
    """
    text_lower = text.lower()
    
    # Intent indicators for each category
    intent_indicators = {
        'informational': {
            'keywords': [
                'what is', 'how to', 'why', 'when', 'where', 'guide', 'tutorial', 'explain', 
                'definition', 'meaning', 'overview', 'introduction', 'basics', 'fundamentals',
                'tips', 'advice', 'learn', 'understand', 'examples', 'types', 'kinds'
            ],
            'patterns': [
                r'\bwhat\b', r'\bhow\b', r'\bwhy\b', r'\bwhen\b', r'\bwhere\b',
                r'\bguide\b', r'\btutorial\b', r'\bexplain\b', r'\bdefinition\b',
                r'\bmeaning\b', r'\boverview\b', r'\bbasics\b', r'\btips\b',
                r'\badvice\b', r'\blearn\b', r'\bunderstand\b', r'\bexamples\b'
            ]
        },
        'navigational': {
            'keywords': [
                'official', 'website', 'homepage', 'login', 'sign up', 'contact',
                'about us', 'company', 'brand', 'product name', 'service name',
                'download', 'app', 'mobile app', 'web app', 'platform'
            ],
            'patterns': [
                r'\bofficial\b', r'\bwebsite\b', r'\bhomepage\b', r'\blogin\b',
                r'\bsign up\b', r'\bcontact\b', r'\babout us\b', r'\bcompany\b',
                r'\bbrand\b', r'\bdownload\b', r'\bapp\b', r'\bplatform\b'
            ]
        },
        'transactional': {
            'keywords': [
                'buy', 'purchase', 'order', 'shop', 'store', 'price', 'cost',
                'discount', 'deal', 'offer', 'sale', 'free trial', 'demo',
                'compare', 'review', 'best', 'top', 'recommend', 'alternative',
                'vs', 'versus', 'alternative', 'competitor'
            ],
            'patterns': [
                r'\bbuy\b', r'\bpurchase\b', r'\border\b', r'\bshop\b', r'\bstore\b',
                r'\bprice\b', r'\bcost\b', r'\bdiscount\b', r'\bdeal\b', r'\boffer\b',
                r'\bsale\b', r'\bfree trial\b', r'\bdemo\b', r'\bcompare\b',
                r'\breview\b', r'\bbest\b', r'\btop\b', r'\brecommend\b'
            ]
        },
        'commercial': {
            'keywords': [
                'review', 'comparison', 'vs', 'versus', 'alternative', 'best',
                'top', 'recommend', 'pros and cons', 'advantages', 'disadvantages',
                'features', 'benefits', 'specifications', 'specs', 'rating',
                'test', 'analysis', 'evaluation'
            ],
            'patterns': [
                r'\breview\b', r'\bcomparison\b', r'\bvs\b', r'\bversus\b',
                r'\balternative\b', r'\bbest\b', r'\btop\b', r'\brecommend\b',
                r'\bpros and cons\b', r'\badvantages\b', r'\bdisadvantages\b',
                r'\bfeatures\b', r'\bbenefits\b', r'\bspecifications\b',
                r'\bspecs\b', r'\brating\b', r'\btest\b', r'\banalysis\b'
            ]
        }
    }
    
    # Calculate intent scores
    intent_scores = {}
    for intent, indicators in intent_indicators.items():
        score = 0
        
        # Count keyword matches
        for keyword in indicators['keywords']:
            if keyword in text_lower:
                score += 2
        
        # Count pattern matches
        for pattern in indicators['patterns']:
            matches = len(re.findall(pattern, text_lower))
            score += matches
        
        intent_scores[intent] = score
    
    # Determine primary intent
    primary_intent = max(intent_scores, key=intent_scores.get)
    primary_score = intent_scores[primary_intent]
    
    # Calculate confidence (0-100)
    total_possible_score = sum(len(indicators['keywords']) * 2 + len(indicators['patterns']) for indicators in intent_indicators.values())
    confidence = min(100, (primary_score / total_possible_score) * 100) if total_possible_score > 0 else 0
    
    # Generate intent-specific recommendations
    intent_recommendations = {
        'informational': [
            "Include clear definitions and explanations of key concepts",
            "Add step-by-step guides or tutorials",
            "Provide examples and use cases",
            "Include a comprehensive FAQ section",
            "Use educational content formats (how-to, what-is, why-does)",
            "Add related topics and concepts for broader coverage"
        ],
        'navigational': [
            "Include clear navigation elements and site structure",
            "Add prominent calls-to-action for key pages",
            "Include contact information and company details",
            "Provide clear links to main sections of your site",
            "Add breadcrumb navigation and site maps",
            "Include brand-specific keywords and company information"
        ],
        'transactional': [
            "Include clear pricing information and purchase options",
            "Add prominent buy buttons and call-to-action elements",
            "Provide product specifications and features",
            "Include customer reviews and testimonials",
            "Add trust signals (security badges, guarantees)",
            "Include shipping and return policy information"
        ],
        'commercial': [
            "Include detailed product comparisons and reviews",
            "Add pros and cons analysis",
            "Provide feature comparisons and specifications",
            "Include expert opinions and third-party reviews",
            "Add comparison tables and charts",
            "Include alternatives and competitor analysis"
        ]
    }
    
    # Get recommendations for primary intent
    recommendations = intent_recommendations.get(primary_intent, [])
    
    # Add secondary intent recommendations if scores are close
    sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)
    if len(sorted_intents) > 1 and sorted_intents[1][1] >= sorted_intents[0][1] * 0.7:
        secondary_intent = sorted_intents[1][0]
        secondary_recommendations = intent_recommendations.get(secondary_intent, [])
        recommendations.extend(secondary_recommendations[:2])  # Add top 2 from secondary intent
    
    return {
        'primary_intent': primary_intent,
        'confidence': round(confidence, 1),
        'intent_scores': intent_scores,
        'recommendations': recommendations[:6]  # Limit to top 6 recommendations
    }

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
    
    # Use regex-based sentence splitter instead of NLTK
    sentences = simple_sent_tokenize(text)
    avg_sentence_length = sum(len(sent.split()) for sent in sentences) / len(sentences) if sentences else 0
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
    
    # Analyze keyword intent
    intent_analysis = analyze_keyword_intent(text)
    
    return {
        'total_score': total_score,
        'category_scores': scores,
        'recommendations': recommendations,
        'intent_analysis': intent_analysis
    }

def extract_content_from_url(url):
    """
    Extract main content and comprehensive metadata from a given URL.
    Returns a dictionary with content and detailed metadata.
    """
    try:
        # Validate URL
        parsed_url = urlparse(url)
        if not parsed_url.scheme or not parsed_url.netloc:
            return {'error': 'Invalid URL format'}
        
        # Set up headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        # Fetch the URL with timeout
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer", "aside"]):
            script.decompose()
        
        # Extract comprehensive metadata
        metadata = extract_metadata(soup, url)
        
        # Try to find the main content area
        main_content = None
        
        # Common selectors for main content
        content_selectors = [
            'article',
            'main',
            '.content',
            '.post',
            '.article',
            '.entry',
            '.post-content',
            '.article-content',
            '.main-content',
            '#content',
            '#main',
            '.blog-post',
            '.blog-entry'
        ]
        
        for selector in content_selectors:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        # If no main content found, try to find the largest text block
        if not main_content:
            # Find all divs with substantial text content
            divs = soup.find_all('div')
            largest_div = None
            max_text_length = 0
            
            for div in divs:
                text_length = len(div.get_text(strip=True))
                if text_length > max_text_length and text_length > 500:  # Minimum 500 characters
                    max_text_length = text_length
                    largest_div = div
            
            if largest_div:
                main_content = largest_div
            else:
                # Fallback to body content
                main_content = soup.find('body') or soup
        
        # Extract text content
        if main_content:
            # Get clean text
            text_content = main_content.get_text(separator=' ', strip=True)
            
            # Clean up extra whitespace
            text_content = re.sub(r'\s+', ' ', text_content).strip()
            
            # Extract dates from content
            content_dates = extract_dates_from_text(text_content)
            
            # Get word count
            word_count = len(text_content.split())
            
            return {
                'success': True,
                'content': text_content,
                'word_count': word_count,
                'url': url,
                'metadata': metadata,
                'content_dates': content_dates
            }
        else:
            return {'error': 'Could not extract content from the page'}
            
    except requests.exceptions.Timeout:
        return {'error': 'Request timed out. The website took too long to respond.'}
    except requests.exceptions.ConnectionError:
        return {'error': 'Connection error. Could not connect to the website.'}
    except requests.exceptions.HTTPError as e:
        return {'error': f'HTTP error: {e.response.status_code}'}
    except requests.exceptions.RequestException as e:
        return {'error': f'Request failed: {str(e)}'}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}

def extract_metadata(soup, url):
    """
    Extract comprehensive metadata from HTML soup.
    """
    metadata = {
        'title': '',
        'description': '',
        'keywords': '',
        'author': '',
        'publish_date': '',
        'modified_date': '',
        'canonical_url': '',
        'og_title': '',
        'og_description': '',
        'og_image': '',
        'og_type': '',
        'twitter_card': '',
        'twitter_title': '',
        'twitter_description': '',
        'twitter_image': '',
        'schema_org': {},
        'language': '',
        'robots': '',
        'viewport': '',
        'charset': '',
        'favicon': '',
        'rss_feeds': [],
        'json_ld': []
    }
    
    # Basic meta tags
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.get_text(strip=True)
    
    # Meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        metadata['description'] = meta_desc.get('content', '')
    
    # Meta keywords
    meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
    if meta_keywords:
        metadata['keywords'] = meta_keywords.get('content', '')
    
    # Author
    meta_author = soup.find('meta', attrs={'name': 'author'})
    if meta_author:
        metadata['author'] = meta_author.get('content', '')
    
    # Publication date
    meta_pub_date = soup.find('meta', attrs={'property': 'article:published_time'})
    if meta_pub_date:
        metadata['publish_date'] = meta_pub_date.get('content', '')
    
    # Modified date
    meta_mod_date = soup.find('meta', attrs={'property': 'article:modified_time'})
    if meta_mod_date:
        metadata['modified_date'] = meta_mod_date.get('content', '')
    
    # Canonical URL
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    if canonical:
        metadata['canonical_url'] = canonical.get('href', '')
    
    # Open Graph tags
    og_title = soup.find('meta', attrs={'property': 'og:title'})
    if og_title:
        metadata['og_title'] = og_title.get('content', '')
    
    og_desc = soup.find('meta', attrs={'property': 'og:description'})
    if og_desc:
        metadata['og_description'] = og_desc.get('content', '')
    
    og_image = soup.find('meta', attrs={'property': 'og:image'})
    if og_image:
        metadata['og_image'] = og_image.get('content', '')
    
    og_type = soup.find('meta', attrs={'property': 'og:type'})
    if og_type:
        metadata['og_type'] = og_type.get('content', '')
    
    # Twitter Card tags
    twitter_card = soup.find('meta', attrs={'name': 'twitter:card'})
    if twitter_card:
        metadata['twitter_card'] = twitter_card.get('content', '')
    
    twitter_title = soup.find('meta', attrs={'name': 'twitter:title'})
    if twitter_title:
        metadata['twitter_title'] = twitter_title.get('content', '')
    
    twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
    if twitter_desc:
        metadata['twitter_description'] = twitter_desc.get('content', '')
    
    twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
    if twitter_image:
        metadata['twitter_image'] = twitter_image.get('content', '')
    
    # Language
    html_tag = soup.find('html')
    if html_tag:
        metadata['language'] = html_tag.get('lang', '')
    
    # Robots
    robots = soup.find('meta', attrs={'name': 'robots'})
    if robots:
        metadata['robots'] = robots.get('content', '')
    
    # Viewport
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        metadata['viewport'] = viewport.get('content', '')
    
    # Charset
    charset = soup.find('meta', attrs={'charset': True})
    if charset:
        metadata['charset'] = charset.get('charset', '')
    
    # Favicon
    favicon = soup.find('link', attrs={'rel': 'icon'}) or soup.find('link', attrs={'rel': 'shortcut icon'})
    if favicon:
        metadata['favicon'] = favicon.get('href', '')
    
    # RSS feeds
    rss_links = soup.find_all('link', attrs={'type': 'application/rss+xml'})
    for rss in rss_links:
        metadata['rss_feeds'].append(rss.get('href', ''))
    
    # JSON-LD structured data
    json_ld_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
    for script in json_ld_scripts:
        try:
            json_data = json.loads(script.string)
            metadata['json_ld'].append(json_data)
        except (json.JSONDecodeError, AttributeError):
            continue
    
    # Extract dates from various sources
    dates = extract_dates_from_metadata(soup)
    if dates.get('publish_date') and not metadata['publish_date']:
        metadata['publish_date'] = dates['publish_date']
    if dates.get('modified_date') and not metadata['modified_date']:
        metadata['modified_date'] = dates['modified_date']
    
    return metadata

def extract_dates_from_metadata(soup):
    """
    Extract dates from various metadata sources.
    """
    dates = {}
    
    # Common date patterns in meta tags
    date_patterns = [
        {'property': 'article:published_time'},
        {'property': 'article:modified_time'},
        {'name': 'article:published_time'},
        {'name': 'article:modified_time'},
        {'property': 'og:updated_time'},
        {'name': 'date'},
        {'name': 'pubdate'},
        {'name': 'lastmod'},
        {'property': 'og:published_time'},
        {'property': 'og:modified_time'}
    ]
    
    for pattern in date_patterns:
        meta_tag = soup.find('meta', attrs=pattern)
        if meta_tag:
            content = meta_tag.get('content', '')
            if 'published' in str(pattern) or 'pubdate' in str(pattern):
                dates['publish_date'] = content
            elif 'modified' in str(pattern) or 'updated' in str(pattern):
                dates['modified_date'] = content
    
    # Look for dates in schema.org structured data
    schema_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
    for script in schema_scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, dict):
                # Check for datePublished and dateModified
                if 'datePublished' in data and not dates.get('publish_date'):
                    dates['publish_date'] = data['datePublished']
                if 'dateModified' in data and not dates.get('modified_date'):
                    dates['modified_date'] = data['dateModified']
                
                # Check for nested objects (like in Article schema)
                if 'mainEntity' in data and isinstance(data['mainEntity'], dict):
                    main_entity = data['mainEntity']
                    if 'datePublished' in main_entity and not dates.get('publish_date'):
                        dates['publish_date'] = main_entity['datePublished']
                    if 'dateModified' in main_entity and not dates.get('modified_date'):
                        dates['modified_date'] = main_entity['dateModified']
        except (json.JSONDecodeError, AttributeError):
            continue
    
    return dates

def extract_dates_from_text(text):
    """
    Extract dates from text content using regex patterns.
    """
    dates = []
    
    # Common date patterns
    date_patterns = [
        # ISO format: 2023-12-25
        r'\b\d{4}-\d{2}-\d{2}\b',
        # US format: 12/25/2023
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        # European format: 25/12/2023
        r'\b\d{1,2}/\d{1,2}/\d{4}\b',
        # Month name format: December 25, 2023
        r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b',
        # Abbreviated month: Dec 25, 2023
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b',
        # Relative dates: "2 days ago", "last week", etc.
        r'\b(?:yesterday|today|tomorrow|last\s+(?:week|month|year)|next\s+(?:week|month|year)|(\d+)\s+(?:days?|weeks?|months?|years?)\s+ago)\b'
    ]
    
    for pattern in date_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if match not in dates:
                dates.append(match)
    
    return dates[:10]  # Limit to first 10 dates found

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

@app.route('/fetch-url', methods=['POST'])
def fetch_url():
    url = request.json.get('url', '')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
    
    result = extract_content_from_url(url)
    return jsonify(result)

if __name__ == '__main__':
    # Development settings
    app.run(debug=False, host='0.0.0.0', port=5000) 