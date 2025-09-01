import './App.css';
import React, { useState, useEffect, useCallback } from 'react';


const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = SpeechRecognition ? new SpeechRecognition() : null;


function App() {
// * State variables
// Explanation: These hold all dynamic data used across the app, updated using their respective set functions.
const [prompt, setPrompt] = useState(''); // * Stores user input text or speech transcript. Used in handleSend and cleared after sending.
const [messages, setMessages] = useState([]); // * Stores chat history as array of {text, sender}. Used for chat display and GPT context.
const [emotion, setEmotion] = useState('neutral'); // * Stores current assistant mood. Used in emoji-face display.
const [voices, setVoices] = useState([]); // * Stores available system TTS voices. Used in voice selector dropdown and speakText.
const [selectedVoice, setSelectedVoice] = useState(null); // * Stores chosen voice for TTS. Used when speaking text.
const [currentTime, setCurrentTime] = useState(new Date()); // * Stores current Date object. Used in clock display and updated every second.
const [constantWeather, setConstantWeather] = useState(null); // * Stores background weather info. Used in weather bar display.
const [listening, setListening] = useState(false); // * Stores mic listening state. Used in mic button and speech recognition control.

  // ! Load available voices
  // Explanation: Loads system voices for text-to-speech (TTS). Updates when voices become available.
  useEffect(() => {
    const synth = window.speechSynthesis;

    const loadVoices = () => {
      const availableVoices = synth.getVoices();
      setVoices(availableVoices);
      if (!selectedVoice && availableVoices.length > 0)
        setSelectedVoice(availableVoices[0].name);
    };

    loadVoices();
    if (synth.onvoiceschanged !== undefined)
      synth.onvoiceschanged = loadVoices;
  }, [selectedVoice]);



  // ! Update clock
  // Explanation: Runs every second to update the displayed clock.
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000); // c
    return () => clearInterval(timer); // cleanup
  }, []);



  // ! Fetch weather every 5 minutes
  // Explanation: Keeps the weather info refreshed in the background.
  useEffect(() => {
    fetchConstantWeather();
    const interval = setInterval(fetchConstantWeather, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);



  // * Speak text with chosen voice
  // Explanation: Uses SpeechSynthesis API to read out GPT/weather/news messages.
  const speakText = (text) => {
    if (!('speechSynthesis' in window)) return;
    const utterance = new SpeechSynthesisUtterance(text);
    const voiceObj = voices.find((v) => v.name === selectedVoice);
    if (voiceObj) utterance.voice = voiceObj;
    window.speechSynthesis.speak(utterance);
  };



  // * Build context for GPT
  // Explanation: Prepares chat history so GPT remembers conversation flow.
  const generateContext = () =>
    messages
      .map(
        (msg) =>
          (msg.sender === 'user' ? 'User: ' : 'Assistant: ') + msg.text
      )
      .join(' - ');



  // ! Request news
  // Explanation: Fetches news headlines from /news endpoint and reads them aloud.
  const handleNewsRequest = async () => {
    try {
      const res = await fetch('/news');
      if (!res.ok) throw new Error(`News server error: ${res.status}`);
      const data = await res.json();

      if (data && Array.isArray(data.headlines) && data.headlines.length > 0) {
        let newsText = 'Here are the latest news headlines:';
        data.headlines.slice(0, 3).forEach((h, i) => {
          newsText += ` ${i + 1}. ${h}.`;
        });

        setMessages((prev) => [...prev, { text: newsText, sender: 'gpt' }]);
        speakText(newsText);
        setEmotion('excited');
      } else {
        const errorMsg = 'No recent news headlines available.';
        setMessages((prev) => [...prev, { text: errorMsg, sender: 'gpt' }]);
        speakText(errorMsg);
        setEmotion('sad');
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { text: 'News service temporarily unavailable.', sender: 'gpt' },
      ]);
      speakText('News service temporarily unavailable.');
      setEmotion('sad');
    }
  };



  // ! Constant weather fetch
  // Explanation: Gets weather info for background display (not as a chat message).
  const fetchConstantWeather = async () => {
    try {
      const res = await fetch('/weather');
      if (!res.ok) throw new Error('Weather server error');
      const data = await res.json();

      let weatherText = data.weather
        ? `${data.weather.location ?? data.weather.city ?? 'Your area'}: ${
            data.weather.tempC ?? data.weather.temp ?? '?'
          }°C, ${data.weather.condition ?? 'Unknown'}`
        : 'Weather unavailable';

      setConstantWeather(weatherText);
    } catch (err) {
      console.error(err);
      setConstantWeather('Weather service unavailable');
    }
  };



  // ! Request weather
  // Explanation: Fetches weather info and adds it as a chat message + TTS.
  const handleWeatherRequest = async () => {
    try {
      const res = await fetch('/weather');
      if (!res.ok) throw new Error('Weather server error');
      const data = await res.json();

      let weatherText = data.weather
        ? `Current weather in ${
            data.weather.location ?? data.weather.city ?? 'Your area'
          }: ${data.weather.tempC ?? data.weather.temp ?? '?'}°C, ${
            data.weather.condition ?? 'Unknown'
          }`
        : 'Weather unavailable';

      setMessages((prev) => [...prev, { text: weatherText, sender: 'gpt' }]);
      speakText(weatherText);
      setEmotion('happy');
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { text: 'Weather service temporarily unavailable.', sender: 'gpt' },
      ]);
      speakText('Weather service temporarily unavailable.');
      setEmotion('sad');
    }
  };



  // ! GPT request
  // Explanation: Sends user input + context to GPT backend, then displays + speaks the response.
  const handleGPTRequest = async (inputText) => {
    try {
      const context = generateContext();
      const res = await fetch('/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: inputText, context }),
      });
      if (!res.ok) throw new Error(`GPT service error: ${res.status}`);
      const data = await res.json();

      setMessages((prev) => [...prev, { text: data.text, sender: 'gpt' }]);
      setEmotion(data.emotion);
      speakText(data.text);
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { text: 'Chat service temporarily unavailable.', sender: 'gpt' },
      ]);
      speakText('Chat service temporarily unavailable.');
      setEmotion('sad');
    }
  };



  // ! Handle send (wrapped with useCallback to satisfy ESLint)
  // Explanation: Determines if input is for weather, news, or GPT. Then triggers the correct request.
  const handleSend = useCallback(
    async (inputText = prompt) => {
      if (!inputText.trim()) return;

      setMessages((prev) => [...prev, { text: inputText, sender: 'user' }]);

      const lowerPrompt = inputText.toLowerCase();
      const isWeatherCommand =
        lowerPrompt.includes('weather') ||
        lowerPrompt.includes('forecast') ||
        lowerPrompt.includes('clima');

      const isNewsCommand =
        lowerPrompt.includes('news') || lowerPrompt.includes('headline');

      if (isWeatherCommand) await handleWeatherRequest();
      else if (isNewsCommand) await handleNewsRequest();
      else await handleGPTRequest(inputText);

      setPrompt('');
    },
    [prompt, messages, voices, selectedVoice]
  );



  // ! Speech recognition handlers
  // Explanation: Sets up recognition (language, interim/final results, start/stop events).
  useEffect(() => {
    if (!recognition) return;

    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setListening(true);
    };

    recognition.onend = () => {
      setListening(false);
    };

    recognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          transcript += event.results[i][0].transcript;
        }
      }
      if (transcript.trim() !== '') {
        handleSend(transcript);
      }
    };
  }, [recognition, handleSend]);



  // ! Toggle microphone
  // Explanation: Starts or stops listening when mic button is pressed.
  const toggleListening = () => {
    if (!recognition) return;
    if (listening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  };

// * ------------------------------------------UI RENDERING------------------------------------------ *

  return (
    <div className="app-container">
      {/* Clock display */}
      <div className="clock">{currentTime.toLocaleTimeString()}</div>

      {/* Weather display */}
      <div className="weather">
        🌤️ {constantWeather || 'Loading weather...'}
      </div>

      <h1 className="title">Smart Mirror Assistant</h1>

      {/* ! Mic button instead of input */}
      <div className="input-section">
        <button onClick={toggleListening}>
          {listening ? '🛑 Stop Listening' : '🎙️ Talk'}
        </button>
      </div>

      {/* Voice selector */}
      <div className="voice-selector">
        <label>Select voice: </label>
        <select
          value={selectedVoice || ''}
          onChange={(e) => setSelectedVoice(e.target.value)}
        >
          {voices.map((v, i) => (
            <option key={i} value={v.name}>
              {v.name} ({v.lang})
            </option>
          ))}
        </select>
      </div>

      {/* Chat section */}
      <div className="chat-section">
        {messages.map((msg, idx) => (
          <div key={idx} className={`chat-message ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
      </div>

      {/* Emoji face (mood indicator) */}
      <div className="emoji-face">
        {emotion === 'happy'
          ? '😊'
          : emotion === 'sad'
          ? '😢'
          : emotion === 'angry'
          ? '😠'
          : emotion === 'excited'
          ? '🤩'
          : '😐'}
      </div>
    </div>
  );
}

export default App;
