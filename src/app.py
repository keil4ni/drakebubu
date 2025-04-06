from flask import Flask, request, jsonify
from flask_cors import CORS
from main import search_song, scrape_lyrics_from_url, analyze_sentiment, match_labubu, ACCESS_TOKEN

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.after_request
def apply_cors(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response

@app.route('/analyze', methods=['POST', 'OPTIONS'])
def analyze():
    if request.method == 'OPTIONS':
        return '', 204  # respond to preflight with no content

    data = request.get_json()
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
    app.run(debug=True, port=5000)
