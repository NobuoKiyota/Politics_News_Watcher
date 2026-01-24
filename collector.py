import feedparser
import urllib.parse
import trafilatura
import hashlib
import time

def get_news_rss(keyword, when='1d'):
    """
    Fetch news from Google News RSS.
    """
    encoded_keyword = urllib.parse.quote(keyword)
    rss_url = f"https://news.google.com/rss/search?q={encoded_keyword}+when:{when}&hl=ja&gl=JP&ceid=JP:ja"
    print(f"DEBUG: RSS URL: {rss_url}")
    feed = feedparser.parse(rss_url)
    if not feed.entries:
        print(f"DEBUG: No entries found. Feed status: {getattr(feed, 'status', 'Unknown')}")
    return feed.entries

def generate_article_id(link):
    import hashlib
    return hashlib.md5(link.encode('utf-8')).hexdigest()

def extract_content(url):
    """
    Extract main text content from a URL using Trafilatura.
    """
    try:
        # Use requests with headers to mimic browser and follow redirects
        import requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # 1. Fetch with requests to handle redirects and blocks
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            html_content = response.text
            final_url = response.url # Resolved URL
        except Exception as req_e:
            print(f"    Request failed: {req_e}")
            return None

        # 2. Extract using Trafilatura on the HTML
        text = trafilatura.extract(html_content, include_comments=False, include_tables=False)
        
        if text and len(text) > 50:
            return text
            
        print("    Trafilatura failed, trying BeautifulSoup fallback...")
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        text = soup.get_text(separator='\n')
        
        # Clean up lines
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if len(text) > 100:
             return text
             
        return None
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None

def generate_article_id(url):
    """
    Generate a unique ID for the article based on URL hash.
    """
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def collect_news_for_keyword(keyword):
    """
    Main function to collect news for a keyword.
    Returns a list of dictionaries with title, link, content, etc.
    """
    print(f"Collecting news for: {keyword}")
    entries = get_news_rss(keyword)
    news_items = []
    
    for entry in entries:
        try:
            title = entry.title
            link = entry.link
            published = entry.published
            article_id = generate_article_id(link)

            print(f"  - Found: {title}")
            # Attempt extraction
            content = extract_content(link)
            
            # Fallback: If extraction failed, use RSS summary/description
            if not content:
                print(f"    -> Extraction failed, using RSS summary.")
                content = entry.get('summary', '') or entry.get('description', '') or entry.get('title', '')
                # If still empty?
                if not content:
                    content = "Content Unavailable"

            # Check duplication locally or just collect?
            # Collector simply collects. Duplication check is in job_runner.
            
            news_items.append({
                'id': article_id,
                'title': title,
                'link': link,
                'published': published,
                'content': content
            })
            print(f"    -> Collected (Length: {len(content)})")
            time.sleep(1) # Be polite to servers
            
        except Exception as e:
            print(f"    Error processing entry: {e}")
            
    return news_items

if __name__ == "__main__":
    # Test
    data = collect_news_for_keyword("岸田文雄")
    print(f"Collected {len(data)} articles.")
