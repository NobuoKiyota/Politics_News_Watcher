import base64
import functools
import re

def decode_google_news_url(source_url):
    """
    Decodes the Google News intermediate URL to find the original source URL.
    """
    try:
        # Check standard format
        if "news.google.com" not in source_url:
            return source_url
            
        print(f"DEBUG: Decoding {source_url}")
        # Extract the ID part (e.g. CBMidkFVX...)
        # Usually between 'articles/' and '?'
        match = re.search(r'articles/([a-zA-Z0-9_\-]+)', source_url)
        if not match:
             print("DEBUG: No base64 match found.")
             return source_url
            
        base64_str = match.group(1)
        print(f"DEBUG: Base64 candidate: {base64_str[:10]}...")
        
        # Decode base64
        # Padding adjustments might be needed
        pad = len(base64_str) % 4
        if pad == 1:
            base64_str = base64_str[:-1] # Strip invalid? Or add? 
            # Usually URL safe base64 uses - and _
        elif pad == 2:
            base64_str += '=='
        elif pad == 3:
            base64_str += '='
            
        decoded_bytes = base64.urlsafe_b64decode(base64_str)
        decoded_str = decoded_bytes.decode('latin1') # Often contains binary garbage + URL
        
        # Extract URL from decoded string
        # It usually starts with http/https and ends with some control char or is null terminated
        # Regex to find longest url
        url_match = re.search(r'(https?://[a-zA-Z0-9./_\-%]+)', decoded_str)
        
        if url_match:
            found_url = url_match.group(1)
            print(f"  [Decoder] Resolved: {source_url[:30]}... -> {found_url}")
            return found_url
        
        # Fallback: Just return original if decoding didn't yield a URL
        return source_url
        
    except Exception as e:
        print(f"  [Decoder Error] {e}")
        return source_url
