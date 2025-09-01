# news_service.py
import requests

# ! Configuration - NewsAPI key for accessing news data
NEWS_API_KEY = "3aab2640c7a248ac8d85bdf2692412b4"  # * Your valid API key

# ! Main function to fetch news headlines
def get_news_headlines():
    """
    Fetches news headlines with focus on soccer (Portugal) and technology.
    Returns a list of headline strings.
    Returns an empty list if there's an error.
    """
    try:
        # ! Soccer/Football news URLs - Priority: Portugal focus
        soccer_urls = [
            # * Portugal-specific football searches
            f"https://newsapi.org/v2/everything?q=portugal+football&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}",
            f"https://newsapi.org/v2/everything?q=portugal+soccer&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}",
            f"https://newsapi.org/v2/everything?q=portugal+liga&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}",
            f"https://newsapi.org/v2/everything?q=benfica+porto+sporting&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}",
            # * General football/soccer searches
            f"https://newsapi.org/v2/everything?q=premier+league+champions+league&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}",
            f"https://newsapi.org/v2/top-headlines?category=sports&language=en&apiKey={NEWS_API_KEY}"
        ]
        
        # ! Technology news URLs - Secondary priority
        tech_urls = [
            f"https://newsapi.org/v2/top-headlines?category=technology&language=en&apiKey={NEWS_API_KEY}",
            f"https://newsapi.org/v2/everything?q=technology+ai+programming&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}",
            f"https://newsapi.org/v2/everything?q=apple+google+microsoft&language=en&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
        ]
        
        all_headlines = []  # * Collection bucket for all headlines
        
        # ! Phase 1: Fetch soccer news first
        print("[NEWS API] Searching for soccer/football news...")
        for url in soccer_urls:
            try:
                response = requests.get(url, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok' and data.get('articles'):
                        # * Filter out invalid articles
                        headlines = [
                            article['title'] for article in data['articles'] 
                            if article['title'] != '[Removed]' and article['title']
                        ]
                        if headlines:
                            print(f"[SOCCER] Found {len(headlines)} headlines")
                            all_headlines.extend(headlines)
                            if len(all_headlines) >= 5:  # * Enough soccer content
                                break
            except:
                continue  # * Skip failed URLs
        
        # ! Phase 2: Fetch technology news
        print("[NEWS API] Searching for technology news...")
        for url in tech_urls:
            try:
                response = requests.get(url, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'ok' and data.get('articles'):
                        headlines = [
                            article['title'] for article in data['articles'] 
                            if article['title'] != '[Removed]' and article['title']
                        ]
                        if headlines:
                            print(f"[TECH] Found {len(headlines)} headlines")
                            all_headlines.extend(headlines)
                            if len(all_headlines) >= 8:  # * Total limit reached
                                break
            except:
                continue
        
        # ! Process results: deduplicate and limit
        unique_headlines = []
        seen = set()  # * Track duplicates
        for headline in all_headlines:
            if headline not in seen and len(unique_headlines) < 8:
                seen.add(headline)
                unique_headlines.append(headline)
        
        print(f"[NEWS API] Total unique headlines: {len(unique_headlines)}")
        return unique_headlines
        
    except requests.exceptions.RequestException as e:
        # ? Network or API connection issues
        print(f"[NEWS API] Request Failed: {e}")
        return []
    except Exception as e:
        # ? Unexpected errors during processing
        print(f"[NEWS API] Unexpected error: {e}")
        return []

# ! Test function when run directly
if __name__ == "__main__":
    print("Testing News Service - Soccer & Technology Focus...")
    print("=" * 50)
    
    headlines = get_news_headlines()
    
    if headlines:
        print("\n🎯 Final News Headlines:")
        print("=" * 50)
        for i, headline in enumerate(headlines, 1):
            # * Categorize with emojis for visual identification
            soccer_keywords = ['soccer', 'portugal', 'benfica', 'porto', 'sporting', 'liga', 'champions', 'premier']
            is_soccer = any(keyword.lower() in headline.lower() for keyword in soccer_keywords)
            
            tech_keywords = ['tech', 'ai', 'apple', 'google', 'microsoft', 'programming', 'software', 'computer']
            is_tech = any(keyword.lower() in headline.lower() for keyword in tech_keywords)
            
            emoji = "⚽" if is_soccer else "💻" if is_tech else "📰"
            print(f"{emoji} {i}. {headline}")
    else:
        print("❌ Failed to get news headlines.")