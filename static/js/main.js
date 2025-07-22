class KrishiAI {
    constructor() {
        this.isRecording = false;
        this.recognition = null;
        this.currentLanguage = 'english';
        this.userId = this.generateUserId();
        
        this.initializeElements();
        this.initializeSpeechRecognition();
        this.bindEvents();
    }

    initializeElements() {
        this.voiceButton = document.getElementById('voiceButton');
        this.textInput = document.getElementById('textInput');
        this.sendButton = document.getElementById('sendButton');
        this.languageSelect = document.getElementById('languageSelect');
        this.loading = document.getElementById('loading');
        this.status = document.getElementById('status');
        this.responseSection = document.getElementById('responseSection');
        this.responseText = document.getElementById('responseText');
        this.audioPlayer = document.getElementById('audioPlayer');
    }

    generateUserId() {
        return 'user_' + Math.random().toString(36).substr(2, 9);
    }

    initializeSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            
            this.recognition.onstart = () => {
                this.isRecording = true;
                this.voiceButton.classList.add('recording');
                this.voiceButton.innerHTML = '<i class="fas fa-stop"></i>';
                this.showStatus('Listening... Speak now!', 'success');
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                this.textInput.value = transcript;
                this.askQuestion(transcript);
            };

            this.recognition.onerror = (event) => {
                this.showStatus('Speech recognition error: ' + event.error, 'error');
                this.stopRecording();
            };

            this.recognition.onend = () => {
                this.stopRecording();
            };

            // Set language based on selection
            this.updateRecognitionLanguage();
        } else {
            this.showStatus('Speech recognition not supported in this browser', 'error');
        }
    }

    updateRecognitionLanguage() {
        if (this.recognition) {
            const languageMap = {
                'english': 'en-US',
                'hindi': 'hi-IN',
                'kannada': 'kn-IN',
                'tamil': 'ta-IN',
                'telugu': 'te-IN',
                'marathi': 'mr-IN'
            };
            
            this.recognition.lang = languageMap[this.currentLanguage] || 'en-US';
        }
    }

    bindEvents() {
        if (this.voiceButton) {
            this.voiceButton.addEventListener('click', () => this.toggleRecording());
        }
        
        if (this.sendButton) {
            this.sendButton.addEventListener('click', () => this.handleSendMessage());
        }
        
        if (this.textInput) {
            this.textInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.handleSendMessage();
                }
            });
        }
        
        if (this.languageSelect) {
            this.languageSelect.addEventListener('change', (e) => {
                this.currentLanguage = e.target.value;
                if (this.recognition) {
                    this.recognition.lang = this.getRecognitionLanguage();
                }
            });
        }
    }

    startRecording() {
        if (this.recognition) {
            this.recognition.start();
        } else {
            this.showStatus('Speech recognition not available', 'error');
        }
    }

    stopRecording() {
        this.isRecording = false;
        this.voiceButton.classList.remove('recording');
        this.voiceButton.innerHTML = '<i class="fas fa-microphone"></i>';
        
        if (this.recognition) {
            this.recognition.stop();
        }
    }

    async handleSendMessage() {
        const message = this.textInput ? this.textInput.value.trim() : '';
        if (!message) return;
        
        // Clear input
        if (this.textInput) {
            this.textInput.value = '';
        }
        
        // Get weather context if available
        let weatherContext = null;
        if (typeof getWeatherContext === 'function') {
            try {
                weatherContext = await getWeatherContext();
            } catch (error) {
                console.error('Error getting weather context:', error);
            }
        }
        
        // Prepare message data with weather context
        const messageData = {
            question: message,
            language: this.currentLanguage,
            use_voice: true,
            location: weatherContext
        };
        
        // Send the message
        this.askQuestion(message, messageData);
    }

    async askQuestion(question, messageData = null) {
        if (!question && !messageData) return;
        
        this.showLoading(true);
        if (!messageData) {
            this.textInput.value = '';
        }
        
        try {
            // If messageData is provided, use it directly
            const requestData = messageData || {
                question: question,
                language: this.currentLanguage,
                use_voice: true
            };
            
            const response = await fetch('/api/ask', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(requestData)
            });
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const data = await response.json();
            
            // Display response with audio if available
            this.displayResponse(data.answer, data.audio_url);
            
            // If we have weather context, show a note about it
            if (messageData && messageData.location) {
                this.showStatus('Included local weather in your question', 'info');
            }
            
        } catch (error) {
            console.error('Error:', error);
            this.showStatus('Error: Could not get response from server', 'error');
        } finally {
            this.showLoading(false);
        }
    }

    displayResponse(answer, audioUrl = null) {
        if (!this.responseText) return;
        
        // Update the response text
        this.responseText.textContent = answer;
        
        // Show the response section if it exists
        if (this.responseSection) {
            this.responseSection.style.display = 'block';
        }

        // Play audio if URL is provided
        if (audioUrl) {
            this.playAudio(audioUrl);
        }

        // Clear input if it exists
        if (this.textInput) {
            this.textInput.value = '';
        }
        
        // Show success status
        this.showStatus('Response received!', 'success');
        setTimeout(() => this.hideStatus(), 3000);
    }

    displayOfflineResponse(question) {
        const offlineResponses = {
            crop: "For current season, consider growing rice, cotton, or maize. Consult your local agricultural officer for specific recommendations.",
            pest: "Common pests include aphids and bollworm. Use neem oil or pheromone traps. Contact agricultural experts for severe infestations.",
            disease: "Plant diseases like blight and rust are common. Improve drainage and use appropriate fungicides. Seek expert advice for identification.",
            weather: "Monitor weather forecasts regularly. Protect crops during extreme weather. Plan irrigation based on rainfall predictions.",
            default: "I'm here to help with farming questions! Ask about crops, pests, diseases, or farming practices. For complex issues, consult local agricultural experts."
        };

        const questionLower = question.toLowerCase();
        let response = offlineResponses.default;

        if (questionLower.includes('crop') || questionLower.includes('grow') || questionLower.includes('plant')) {
            response = offlineResponses.crop;
        } else if (questionLower.includes('pest') || questionLower.includes('insect') || questionLower.includes('bug')) {
            response = offlineResponses.pest;
        } else if (questionLower.includes('disease') || questionLower.includes('sick') || questionLower.includes('spots')) {
            response = offlineResponses.disease;
        } else if (questionLower.includes('weather') || questionLower.includes('rain') || questionLower.includes('drought')) {
            response = offlineResponses.weather;
        }

        this.responseText.textContent = response;
        this.responseSection.style.display = 'block';
        this.textInput.value = '';
        
        this.showStatus('Offline response provided', 'success');
        setTimeout(() => this.hideStatus(), 3000);
    }

    playAudio(audioData) {
        if (!audioData) return;
        
        try {
            // Create audio element
            const audio = new Audio(audioData);
            
            // Handle audio playback
            audio.play().catch(error => {
                console.error('Error playing audio:', error);
                this.showStatus('Error playing audio', 'error');
            });
            
            // Clean up after playback
            audio.onended = () => {
                audio.remove();
            };
        } catch (error) {
            console.error('Error initializing audio:', error);
        }
    }

    showLoading(show) {
        this.loading.style.display = show ? 'block' : 'none';
        this.sendButton.disabled = show;
        this.voiceButton.disabled = show;
    }

    showStatus(message, type) {
        this.status.textContent = message;
        this.status.className = `status ${type}`;
        this.status.style.display = 'block';
    }

    hideStatus() {
        this.status.style.display = 'none';
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new KrishiAI();
});

// Service Worker for offline functionality
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then((registration) => {
                console.log('SW registered: ', registration);
            })
            .catch((registrationError) => {
                console.log('SW registration failed: ', registrationError);
            });
    });
}
