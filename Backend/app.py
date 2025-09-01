from flask import Flask, request, jsonify
from flask_cors import CORS
from gpt_service import get_gpt_response, get_emotion
from news_service import get_news_headlines
from weather_service import get_weather_data
import uuid

app = Flask(__name__)
CORS(app) # * Allow React frontend to call Flask API

# ! Chat endpoint
@app.route("/chat", methods=["POST"]) # * Define route for chat
def chat():
    data = request.get_json() # * Get data from React frontend
    prompt = data.get("prompt", "") # * Get the current user prompt from React frontend
    context = data.get("context", "") # * Get the conversation context from React frontend
    
    # ! GPT response using context and current prompt
    gpt_text = get_gpt_response(prompt, context) # * Pass context to GPT using get_gpt_response function from gpt_service
    
    # ! Emotion extraction
    emotion = get_emotion(gpt_text) # * Get emotion from GPT response using get_emotion function from gpt_service
    
    # ! Return response
    return jsonify({
        "text": gpt_text, # * Return GPT response text to React frontend
        "emotion": emotion, # * Return emotion to React frontend
    })

# ! News endpoint
@app.route("/news")
def news():
    try:
        # * Get news headlines from news service
        headlines = get_news_headlines()
        
        # ! FIX: Return empty array instead of error if no headlines
        if headlines and len(headlines) > 0:
            return jsonify({"headlines": headlines})
        else:
            # * Return empty headlines array instead of error
            return jsonify({"headlines": []})
            
    except Exception as e:
        print(f"[App News Error] {e}") # * Debug: Print the actual error
        # ! FIX: Return empty array instead of 500 error
        return jsonify({"headlines": []})

# ! Weather endpoint
@app.route("/weather")
def weather():
    try:
        # * Get weather data from weather service
        data = get_weather_data()
        
        # ! Return weather data if available
        if data:
            return jsonify(data)
        else:
            # * Return error if weather data not available
            return jsonify({"error": "Weather data not available"}), 500
            
    except Exception as e:
        print(f"[App Weather Error] {e}") # * Debug: Print the actual error
        # ! Return error response
        return jsonify({"error": "Failed to fetch weather"}), 500
    
if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)