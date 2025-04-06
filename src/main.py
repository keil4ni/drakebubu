import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
from transformers import pipeline
import torch
import gc
import time

# ========= CONFIG ========= #
ACCESS_TOKEN = 'hqBfz2Nc96QV922NM5E8VMK4jBR_DRTEnjPp9p82tbpuGFSKSFEYMVTNXxhygXJh'


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



emotion_classifier = pipeline(
    "text-classification",
    model = "j-hartmann/emotion-english-distilroberta-base",
    top_k = None,
    device =- 1
)
def analyze_sentiment(text):
   

    results = emotion_classifier(text[:512])
    emotion_scores = results[0]
    top_emotion = max(emotion_scores, key=lambda x: x['score'])
    return {
        "top_emotion": top_emotion['label'],
        "confidence": round(top_emotion['score'], 3),
        "all_emotions": {e['label']: round(e['score'], 3) for e in emotion_scores}
    }
# ========= LABUBU MATCHING TO DO: Change========= #
def match_labubu(sentiment_score):
    top_emotions = list(sentiment_score["all_emotions"].items())
    
    top_emotions.sort(key=lambda x: x[1], reverse=True)

    top_3_emotions = [label for label, score in top_emotions[:3]]

    emotion_to_labubu = {
        "joy": "Angel Labubu 😇",
        "sadness": "Sad Labubu 😢",
        "anger": "Devil Labubu 😈",
        "fear": "Dreamy Labubu 🌙",
        "surprise": "Forest Labubu 🌲",
        "neutral": "Sleepy Labubu 😴",
        "disgust": "Grumpy Labubu 😤"
    }

    for emotion in top_3_emotions:
        if emotion in emotion_to_labubu:
            return emotion_to_labubu[emotion]

    return emotion_to_labubu["neutral"]

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
    prediction = match_labubu(sentiment)

    print("\n=== RESULT ===")
    print(f"🎧 Sentiment: {sentiment}")
    print(f"🔮 Your Labubu is: {prediction}")

    top_3 = sorted(sentiment["all_emotions"].items(), key=lambda x: x[1], reverse=True)[:3]
    top_3_str = "\n".join([f"  • {emotion.capitalize()}: {score}" for emotion, score in top_3])

    print("🎧 Top Emotions:")
    print(top_3_str)
    
    print("✅ Script finished without crash.")
    time.sleep(1)

# ========= RUN ========= #
if __name__ == "__main__":
    run_labubu_matcher()
