import requests
from bs4 import BeautifulSoup
from textblob import TextBlob

# ========= CONFIG ========= #
ACCESS_TOKEN = 'hqBfz2Nc96QV922NM5E8VMK4jBR_DRTEnjPp9p82tbpuGFSKSFEYMVTNXxhygXJh'

# ========= LABUBU DATABASE TO DO: CHANGE========= #
labubus = [
    {"name": "Forest Labubu", "vibe": "peaceful, nature, calm, gentle"},
    {"name": "Confident Labubu", "vibe": "assured, bold, positive, fearless"},
    {"name": "Dreamy Labubu", "vibe": "whimsical, soft, fantasy, surreal"},
    {"name": "Angel Labubu", "vibe": "pure, light, innocent, sweet"}
]

# ========= GENIUS API SEARCH THIS WORKS ========= #
def search_song(song_title, access_token):
    base_url = "https://api.genius.com"
    headers = {'Authorization': f'Bearer {access_token}'}
    search_url = f"{base_url}/search"
    params = {'q': song_title}

    response = requests.get(search_url, params=params, headers=headers)
    results = response.json()
    hits = results['response']['hits']

    if not hits:
        return None

    song_info = hits[0]['result']
    return {
        'title': song_info['title'],
        'artist': song_info['primary_artist']['name'],
        'url': song_info['url']
    }

# ========= SCRAPE LYRICS ========= #
def scrape_lyrics_from_url(song_url):
    response = requests.get(song_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    if containers:
        lyrics = "\n".join([c.get_text(separator="\n") for c in containers])
        return lyrics.strip()

    legacy = soup.find("div", class_="lyrics")
    if legacy:
        return legacy.get_text(separator="\n").strip()

    return None

# ========= SENTIMENT ANALYSIS ========= #
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment
    return {
        "polarity": sentiment.polarity,
        "subjectivity": sentiment.subjectivity
    }

# ========= LABUBU MATCHING TO DO: Change========= #
def match_labubu(lyrics, sentiment_score):
    keywords = lyrics.lower().split()
    match_scores = []
    for labubu in labubus:
        vibe_words = labubu["vibe"].split(", ")
        score = sum(word in keywords for word in vibe_words)
        match_scores.append((labubu["name"], score))
    
    match_scores.sort(key=lambda x: x[1], reverse=True)

    if sentiment_score["polarity"] < -0.2:
        return "Devil Labubu 😈"
    elif sentiment_score["polarity"] > 0.5:
        return "Angel Labubu 😇"
    elif match_scores[0][1] > 0:
        return match_scores[0][0]
    else:
        return "Dreamy Labubu 🌙"

# ========= MAIN FUNCTION ========= #
def run_labubu_matcher():
    song_input = input("🎵 Enter a song title and artist: ")
    print("🔍 Searching Genius...")

    song = search_song(song_input, ACCESS_TOKEN)

    if not song:
        print("❌ Song not found.")
        return

    print(f"🎶 Found: {song['title']} by {song['artist']}")
    print("📄 Fetching lyrics...")

    lyrics = scrape_lyrics_from_url(song['url'])


    if not lyrics:
        print("❌ Could not retrieve lyrics.")
        return

    sentiment = analyze_sentiment(lyrics)
    prediction = match_labubu(lyrics, sentiment)

    print("\n=== RESULT ===")
    print(f"🎧 Sentiment: {sentiment}")
    print(f"🔮 Your Labubu is: {prediction}")

# ========= RUN ========= #
if __name__ == "__main__":
    run_labubu_matcher()
