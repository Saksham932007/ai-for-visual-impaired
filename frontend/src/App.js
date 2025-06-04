import React, { useState, useRef, useEffect } from 'react';
import './App.css';

const App = () => {
  const [isStreaming, setIsStreaming] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [currentMode, setCurrentMode] = useState('objects');
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [history, setHistory] = useState([]);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const recognitionRef = useRef(null);

  // Backend URL from environment
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window) {
      const recognition = new window.webkitSpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        const command = event.results[0][0].transcript.toLowerCase();
        handleVoiceCommand(command);
      };

      recognition.onerror = (event) => {
        console.log('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognitionRef.current = recognition;
    }
  }, []);

  // Voice command handler
  const handleVoiceCommand = (command) => {
    speak('Command received: ' + command);
    
    if (command.includes('detect objects') || command.includes('what do you see')) {
      setCurrentMode('objects');
      captureAndAnalyze('objects');
    } else if (command.includes('read text') || command.includes('read this')) {
      setCurrentMode('text');
      captureAndAnalyze('text');
    } else if (command.includes('detect money') || command.includes('currency') || command.includes('how much')) {
      setCurrentMode('currency');
      captureAndAnalyze('currency');
    } else if (command.includes('colors') || command.includes('what color')) {
      setCurrentMode('colors');
      captureAndAnalyze('colors');
    } else if (command.includes('start camera') || command.includes('camera on')) {
      startCamera();
    } else if (command.includes('help') || command.includes('emergency')) {
      handleEmergency();
    } else {
      speak('Sorry, I did not understand that command. Try saying: detect objects, read text, detect money, or colors.');
    }
  };

  // Text-to-speech function
  const speak = (text) => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.9;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      
      speechSynthesis.speak(utterance);
    }
  };

  // Start voice listening
  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      setIsListening(true);
      speak('Listening for your command');
      recognitionRef.current.start();
    }
  };

  // Start camera stream
  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment', // Use back camera on mobile
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsStreaming(true);
        speak('Camera started. You can now use voice commands or tap the action buttons.');
      }
    } catch (error) {
      console.error('Camera access denied:', error);
      speak('Camera access denied. Please allow camera permission and try again.');
    }
  };

  // Capture and analyze frame
  const captureAndAnalyze = async (mode = currentMode) => {
    if (!videoRef.current || !canvasRef.current) {
      speak('Please start the camera first');
      return;
    }
    
    setLoading(true);
    const analysisMode = mode || currentMode;
    
    // Announce what we're doing
    const actionMessages = {
      objects: 'Analyzing objects in your view',
      text: 'Reading text from the image',
      currency: 'Detecting currency and amounts',
      colors: 'Identifying colors'
    };
    
    speak(actionMessages[analysisMode] || 'Analyzing image');
    
    const canvas = canvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    // Convert to blob
    canvas.toBlob(async (blob) => {
      const formData = new FormData();
      formData.append('file', blob, 'capture.jpg');
      
      try {
        const endpoint = `${backendUrl}/api/vision/${analysisMode}`;
        const response = await fetch(endpoint, {
          method: 'POST',
          body: formData
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        setAnalysis(result);
        
        // Speak the results based on mode
        let textToSpeak = '';
        if (analysisMode === 'objects') {
          textToSpeak = result.description;
        } else if (analysisMode === 'text') {
          textToSpeak = result.text_content || 'No text detected';
        } else if (analysisMode === 'currency') {
          textToSpeak = result.description || 'No currency detected';
        } else if (analysisMode === 'colors') {
          textToSpeak = result.color_description || 'Colors not identified';
        }
        
        speak(textToSpeak);
        
        // Add to history
        setHistory(prev => [result, ...prev.slice(0, 4)]);
        
      } catch (error) {
        console.error('Analysis failed:', error);
        speak('Analysis failed. Please try again or check your internet connection.');
      } finally {
        setLoading(false);
      }
    }, 'image/jpeg', 0.8);
  };

  // Emergency SOS handler
  const handleEmergency = () => {
    speak('Emergency mode activated. In a real app, this would contact your emergency contacts.');
    // In a real implementation, this would get user location and send to emergency contacts
  };

  // Stop all speech
  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>🔍 SightMate</h1>
        <p>AI-Powered Visual Assistant</p>
      </header>

      <div className="camera-section">
        <div className="camera-container">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted
            className="camera-video"
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          
          {!isStreaming && (
            <div className="camera-placeholder">
              <div className="camera-icon">📷</div>
              <p>Tap "Start Camera" to begin</p>
            </div>
          )}

          {loading && (
            <div className="loading-overlay">
              <div className="spinner"></div>
              <p>Analyzing...</p>
            </div>
          )}
        </div>

        <div className="camera-controls">
          <button 
            onClick={startCamera} 
            disabled={isStreaming}
            className="btn btn-primary"
          >
            📷 Start Camera
          </button>
          
          <button 
            onClick={startListening} 
            disabled={!isStreaming || isListening}
            className={`btn btn-voice ${isListening ? 'listening' : ''}`}
          >
            {isListening ? '🎤 Listening...' : '🎤 Voice Command'}
          </button>

          {isSpeaking && (
            <button 
              onClick={stopSpeaking}
              className="btn btn-stop"
            >
              🔇 Stop Speaking
            </button>
          )}
        </div>
      </div>

      <div className="action-buttons">
        <button 
          onClick={() => captureAndAnalyze('objects')}
          disabled={!isStreaming || loading}
          className={`btn btn-action ${currentMode === 'objects' ? 'active' : ''}`}
        >
          👁️ Detect Objects
        </button>
        
        <button 
          onClick={() => captureAndAnalyze('text')}
          disabled={!isStreaming || loading}
          className={`btn btn-action ${currentMode === 'text' ? 'active' : ''}`}
        >
          📖 Read Text
        </button>
        
        <button 
          onClick={() => captureAndAnalyze('currency')}
          disabled={!isStreaming || loading}
          className={`btn btn-action ${currentMode === 'currency' ? 'active' : ''}`}
        >
          💰 Detect Money
        </button>
        
        <button 
          onClick={() => captureAndAnalyze('colors')}
          disabled={!isStreaming || loading}
          className={`btn btn-action ${currentMode === 'colors' ? 'active' : ''}`}
        >
          🎨 Identify Colors
        </button>
      </div>

      {analysis && (
        <div className="results-section">
          <h3>Analysis Results:</h3>
          <div className="result-card">
            <div className="result-type">{analysis.type?.toUpperCase()}</div>
            <div className="result-content">
              {analysis.description || analysis.text_content || analysis.color_description}
            </div>
            {analysis.detected_amounts && Object.keys(analysis.detected_amounts).length > 0 && (
              <div className="currency-amounts">
                <strong>Detected Amounts:</strong>
                {Object.entries(analysis.detected_amounts).map(([currency, amounts]) => (
                  <div key={currency}>
                    {currency}: {amounts.join(', ')}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      )}

      <div className="help-section">
        <h3>Voice Commands:</h3>
        <ul>
          <li>"Detect objects" or "What do you see?"</li>
          <li>"Read text" or "Read this"</li>
          <li>"Detect money" or "How much?"</li>
          <li>"Colors" or "What color?"</li>
          <li>"Start camera"</li>
          <li>"Help" for emergency</li>
        </ul>
      </div>

      <div className="emergency-section">
        <button 
          onClick={handleEmergency}
          className="btn btn-emergency"
        >
          🆘 Emergency SOS
        </button>
      </div>
    </div>
  );
};

export default App;
