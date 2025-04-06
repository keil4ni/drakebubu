# app.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from main import search_song, scrape_lyrics_from_url, analyze_sentiment, match_labubu, ACCESS_TOKEN

app = Flask(__name__)
CORS(app, origins=["http://127.0.0.1:5500"])

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    song_input = data.get('song')
    
    song = search_song(song_input, ACCESS_TOKEN)
    if not song:
        return jsonify({'error': 'Song not found'}), 404

    lyrics = scrape_lyrics_from_url(song['url'])
    if not lyrics:
        return jsonify({'error': 'Could not retrieve lyrics'}), 500

    sentiment = analyze_sentiment(lyrics)
    labubu = match_labubu(sentiment)

    return jsonify({
        'song': song,
        'sentiment': sentiment,
        'labubu': labubu
    })

if __name__ == '__main__':
    app.run(debug=True)
