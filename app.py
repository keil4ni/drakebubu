from flask import Flask, request, render_template
from bs4 import BeautifulSoup
from transformers import pipeline
import requests

app = Flask(__name__)

ACCESS_TOKEN = 'hqBfz2Nc96QV922NM5E8VMK4jBR_DRTEnjPp9p82tbpuGFSKSFEYMVTNXxhygXJh'

def search_song(song_title, access_token):
    base_url = "https://api.genius.com"
    headers = {'Authorization': f'Bearer {access_token}'}
    params = {'q': song_title}
    response = requests.get(f"{base_url}/search", params=params, headers=headers)
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

def scrape_lyrics_from_url(song_url):
    response = requests.get(song_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    containers = soup.find_all("div", attrs={"data-lyrics-container": "true"})
    if containers:
        return "\n".join([c.get_text(separator="\n") for c in containers]).strip()
    legacy = soup.find("div", class_="lyrics")
    if legacy:
        return legacy.get_text(separator="\n").strip()
    return None

def analyze_sentiment(text):
    classifier = pipeline(
        "text-classification",
        model="j-hartmann/emotion-english-distilroberta-base",
        top_k=None
    )
    results = classifier(text[:512])[0]
    top_emotion = max(results, key=lambda x: x['score'])
    return {
        "top_emotion": top_emotion['label'],
        "confidence": round(top_emotion['score'], 3),
        "all_emotions": {e['label']: round(e['score'], 3) for e in results}
    }

def match_labubu(emotion):
    emotion_to_image = {
        "joy": ["happy1.png", "happy2.png"],
        "sadness": ["sad1.png", "sad2.png"],
        "anger": ["anger.png"],
        "fear": ["fear.png"],
        "surprise": ["surprised.png"],
        "neutral": ["neutral.png"],
        "disgust": ["disgust.png"],
        "love": ["love1.png", "love2.png"]
    }
    return emotion_to_image.get(emotion.lower(), ["neutral.png"])[0]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/result', methods=['GET'])
def result():
    song_title = request.args.get('song')
    if not song_title:
        return render_template('index.html')

    song = search_song(song_title, ACCESS_TOKEN)
    if not song:
        return render_template('result.html', song=song_title, emotion="unknown", image="neutral.png")

    lyrics = scrape_lyrics_from_url(song['url'])
    if not lyrics:
        return render_template('result.html', song=song_title, emotion="unknown", image="neutral.png")

    sentiment = analyze_sentiment(lyrics)
    emotion = sentiment["top_emotion"]
    image = match_labubu(emotion)

    return render_template('result.html', song=song_title, emotion=emotion, image=image)

if __name__ == '__main__':
    app.run(debug=True)