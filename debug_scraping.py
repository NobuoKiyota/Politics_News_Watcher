import requests
from bs4 import BeautifulSoup
import trafilatura
import url_decoder

URL = "https://news.google.com/rss/articles/CBMidkFVX3lxTE1TZXM3MkwtdzQzZjF0ZmNsV1d3LThvZU5yemNBODgyYWlXc2RrSFRmcXBUZ05Ca3NGTTd4TzV3d1BKQzdFcGRyc2thWnFBcGRnRjVpZWRoWWR0dmF3UlgzX3pOMGFJOEJGUEdub0V2Mzc2MWlBTUE?oc=5"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def test_scrape():
    print(f"Testing Scrape for: {URL}")
    
    # Decode
    decoded_url = url_decoder.decode_google_news_url(URL)
    print(f"Decoded URL: {decoded_url}")
    
    # Use decoded for Request
    final_target_url = decoded_url
    
    try:
        # 1. Requests
        print("1. Sending Request...")
        response = requests.get(final_target_url, headers=HEADERS, timeout=10)
        print(f"   Status Code: {response.status_code}")
        print(f"   Final URL: {response.url}")
        
        if response.status_code != 200:
            print("   -> Request Failed.")
            return

        html = response.text
        print(f"   HTML Length: {len(html)}")
        
        # 2. Trafilatura
        print("2. Trafilatura Extraction...")
        text = trafilatura.extract(html)
        if text:
            print(f"   -> Success. Length: {len(text)}")
            print(f"   HEAD: {text[:100]}...")
        else:
            print("   -> Failed (None returned).")
            
        # 3. BS4
        print("3. BS4 Fallback...")
        soup = BeautifulSoup(html, 'html.parser')
        text_bs = soup.get_text(separator='\n')
        # Simple cleanup
        text_bs = '\n'.join([line.strip() for line in text_bs.splitlines() if line.strip()])
        print(f"   -> BS4 Length: {len(text_bs)}")
        print(f"   HEAD: {text_bs[:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_scrape()
