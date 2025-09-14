# integrated_app.py
# Professional Agricultural Voice Assistant with ChatGPT-like UI

import streamlit as st
import tempfile
import os
import base64
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import io
from datetime import datetime
import time
import json
import threading
import wave
from typing import Dict, List
import html # For escaping user input to prevent HTML injection
import re # To strip HTML tags from input

# Import your existing agricultural assistant
try:
    from farm_bot import AgricultureAssistant  
except ImportError:
    st.error("❌ Could not import AgricultureAssistant. Make sure farm_bot.py is in the same directory.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="AgroAI - Smart Farming Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for ChatGPT-like interface
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main {
        font-family: 'Inter', sans-serif;
        background: #fafafa;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .header-container {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
        padding: 2rem 0;
        border-radius: 0 0 20px 20px;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }
    
    .header-title {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .header-subtitle {
        font-size: 1.2rem;
        font-weight: 300;
        opacity: 0.9;
    }
    
    .chat-container {
        max-height: 60vh;
        overflow-y: auto;
        padding: 1rem;
        background: white;
        border-radius: 15px;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .user-message {
        background: linear-gradient(135deg, #2e7d32 0%, #4caf50 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 4px 18px;
        margin: 0.5rem 0 0.5rem auto;
        max-width: 80%;
        box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
        animation: slideInRight 0.3s ease-out;
        word-wrap: break-word;
    }
    
    .bot-message {
        background: #f5f5f5;
        color: #333;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        margin: 0.5rem auto 0.5rem 0;
        max-width: 80%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        animation: slideInLeft 0.3s ease-out;
        word-wrap: break-word;
    }
    
    .message-time {
        font-size: 0.75rem;
        opacity: 0.7;
        margin-top: 0.5rem;
        text-align: right;
    }
    
    .bot-message .message-time {
        text-align: left;
    }
    
    .audio-indicator {
        display: inline-flex;
        align-items: center;
        background: rgba(255,255,255,0.2);
        padding: 0.3rem 0.8rem;
        border-radius: 12px;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    /* ChatGPT-like Input Container */
    .input-container {
        position: sticky;
        bottom: 0;
        background: white;
        border-radius: 25px;
        padding: 0.75rem 1rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border: 2px solid #e0e0e0;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .input-container:focus-within {
        border-color: #4caf50;
        box-shadow: 0 4px 25px rgba(76, 175, 80, 0.2);
    }
    
    .input-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .text-input {
        flex: 1;
        border: none !important;
        outline: none !important;
        background: transparent !important;
        font-size: 1rem;
        padding: 0.5rem 0;
    }
    
    .voice-button {
        background: #4caf50;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1.1rem;
    }
    
    .voice-button:hover {
        background: #2e7d32;
        transform: scale(1.1);
    }
    
    .voice-button.recording {
        background: #f44336;
        animation: pulse 1.5s infinite;
    }
    
    .send-button {
        background: #4caf50;
        color: white;
        border: none;
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.3s ease;
        font-size: 1.1rem;
    }
    
    .send-button:hover {
        background: #2e7d32;
        transform: scale(1.1);
    }
    
    .send-button:disabled {
        background: #ccc;
        cursor: not-allowed;
        transform: none;
    }
    
    .recording-status {
        background: #f44336;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        margin: 0.5rem 0;
        animation: pulse 1.5s infinite;
        text-align: center;
    }
    
    .stat-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        text-align: center;
        border-left: 4px solid #4caf50;
        transition: transform 0.3s ease;
        margin-bottom: 1rem;
    }
    
    .stat-card:hover {
        transform: translateY(-3px);
    }
    
    .stat-number {
        font-size: 1.8rem;
        font-weight: 700;
        color: #2e7d32;
        display: block;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .audio-player {
        background: linear-gradient(135deg, #2e7d32, #4caf50);
        border-radius: 20px;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
    }
    
    .audio-player audio {
        width: 100%;
        height: 35px;
        border-radius: 15px;
    }
    
    @keyframes slideInRight {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideInLeft {
        from { transform: translateX(-100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    .source-card {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .source-card:hover {
        background: #e9ecef;
        border-color: #4caf50;
    }
    
    .source-header {
        font-weight: 600;
        color: #495057;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .source-content {
        font-size: 0.9rem;
        color: #6c757d;
        line-height: 1.4;
    }
    
    .error-message {
        background: #ffebee;
        color: #c62828;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ffcdd2;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #e8f5e8;
        color: #2e7d32;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c8e6c9;
        margin: 1rem 0;
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem 1.5rem;
        color: #666;
        font-style: italic;
    }
    
    .typing-dots {
        display: flex;
        gap: 3px;
    }
    
    .typing-dots div {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #4caf50;
        animation: typing 1.4s infinite ease-in-out both;
    }
    
    .typing-dots div:nth-child(1) { animation-delay: -0.32s; }
    .typing-dots div:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0); }
        40% { transform: scale(1); }
    }
    
    .welcome-message {
        text-align: center; 
        padding: 3rem 2rem; 
        color: #666;
        background: linear-gradient(135deg, #f5f5f5 0%, #e8f5e8 100%);
        border-radius: 15px;
        margin: 1rem 0;
    }
    
    .welcome-message h3 {
        color: #2e7d32;
        margin-bottom: 1rem;
    }
    
    @media (max-width: 768px) {
        .header-title {
            font-size: 2rem;
        }
        
        .user-message, .bot-message {
            max-width: 95%;
        }
        
        .input-container {
            padding: 0.5rem 0.75rem;
        }
        
        .input-row {
            gap: 0.25rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'assistant' not in st.session_state:
        st.session_state.assistant = None
    if 'assistant_ready' not in st.session_state:
        st.session_state.assistant_ready = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'processing' not in st.session_state:
        st.session_state.processing = False
    if 'recorded_audio' not in st.session_state:
        st.session_state.recorded_audio = None
    if 'recording_thread' not in st.session_state:
        st.session_state.recording_thread = None

def load_assistant():
    """Load the agricultural assistant"""
    try:
        with st.spinner("🌱 Initializing AgroAI Assistant..."):
            assistant = AgricultureAssistant()
            st.session_state.assistant = assistant
            st.session_state.assistant_ready = True
            return True
    except Exception as e:
        st.error(f"❌ Error loading assistant: {str(e)}")
        st.error(f"🔍 Error details: {type(e).__name__}")
        
        # Detailed troubleshooting
        with st.expander("🛠️ Troubleshooting Guide", expanded=True):
            st.markdown("""
            **Common Issues:**
            
            1. **Vector Database Missing:**
               - Run `create_vector_db.py` first
               - Ensure `faiss_index` folder exists
            
            2. **Environment Variables:**
               - Check `.env` file exists
               - Verify all API keys are set
            
            3. **Dependencies:**
               - Install required packages: `pip install -r requirements.txt`
            
            4. **File Paths:**
               - Ensure `farm_bot.py` is in the same directory
               - Check vector database path is correct
            """)
            
            # Show current environment status
            st.markdown("**Environment Status:**")
            env_vars = [
                "AZURE_OPENAI_API_KEY",
                "ENDPOINT_URL", 
                "AZURE_OPENAI_API_KEY_VB",
                "AZURE_ENDPOINT_VB",
                "GROQ_API_KEY"
            ]
            
            for var in env_vars:
                if os.getenv(var):
                    st.success(f"✅ {var} is set")
                else:
                    st.error(f"❌ {var} is missing")
        
        return False

class AudioRecorder:
    """Enhanced audio recorder with better error handling"""
    
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        self.stream = None
    
    def start_recording(self):
        """Start recording audio"""
        try:
            self.recording = True
            self.audio_data = []
            
            def audio_callback(indata, frames, time, status):
                if status:
                    st.warning(f"Audio status: {status}")
                if self.recording:
                    self.audio_data.append(indata.copy())
            
            self.stream = sd.InputStream(
                channels=1,
                samplerate=self.sample_rate,
                callback=audio_callback,
                dtype=np.float32
            )
            self.stream.start()
            return True
            
        except Exception as e:
            st.error(f"❌ Could not start recording: {str(e)}")
            return False
    
    def stop_recording(self):
        """Stop recording and return audio data"""
        try:
            if self.stream and self.recording:
                self.recording = False
                self.stream.stop()
                self.stream.close()
                
                if self.audio_data:
                    # Convert to numpy array
                    audio_array = np.concatenate(self.audio_data, axis=0)
                    # Convert to int16 for WAV format
                    audio_int16 = (audio_array * 32767).astype(np.int16)
                    
                    # Create WAV bytes
                    wav_buffer = io.BytesIO()
                    with wave.open(wav_buffer, 'wb') as wav_file:
                        wav_file.setnchannels(1)
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(self.sample_rate)
                        wav_file.writeframes(audio_int16.tobytes())
                    
                    wav_buffer.seek(0)
                    return wav_buffer.getvalue()
                    
        except Exception as e:
            st.error(f"❌ Error stopping recording: {str(e)}")
        
        return None

def create_temp_audio_file(audio_bytes):
    """Create a temporary audio file from bytes"""
    try:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
        temp_file.write(audio_bytes)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        st.error(f"❌ Error creating temporary file: {str(e)}")
        return None

def display_audio_player(audio_bytes, key_suffix=""):
    """Display audio player with enhanced styling"""
    if audio_bytes:
        try:
            audio_base64 = base64.b64encode(audio_bytes).decode()
            audio_html = f"""
            <div class="audio-player">
                <audio controls style="width: 100%;">
                    <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
                    Your browser does not support the audio element.
                </source>
                </audio>
            </div>
            """
            st.markdown(audio_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"❌ Error displaying audio: {str(e)}")

def add_message_to_chat(message_type, content, audio_bytes=None, sources=None, timestamp=None, is_audio=False):
    """Add message to chat history with proper error handling"""
    if timestamp is None:
        timestamp = datetime.now().strftime("%H:%M")
    
    message = {
        "type": message_type,
        "content": content,
        "audio_bytes": audio_bytes,
        "sources": sources or [],
        "timestamp": timestamp,
        "is_audio": is_audio
    }
    
    st.session_state.chat_history.append(message)

def display_typing_indicator():
    """Display typing indicator"""
    st.markdown("""
    <div class="bot-message typing-indicator">
        <div>🤖 AgroAI is thinking</div>
        <div class="typing-dots">
            <div></div>
            <div></div>
            <div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_chat_history():
    """Display chat history with enhanced UI"""
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="welcome-message">
            <h3>👋 Welcome to AgroAI!</h3>
            <p>Your intelligent farming companion is ready to help!</p>
            <p><strong>Ask me about:</strong></p>
            <div style="margin-top: 1rem;">
                🌱 Crop cultivation techniques<br>
                🐛 Pest management solutions<br>
                🌾 Fertilizer recommendations<br>
                🌦️ Weather-related farming advice<br>
                📚 Training programs and resources
            </div>
            <div style="margin-top: 1.5rem; font-size: 0.9rem; color: #888;">
                Type your question below or click the microphone to speak
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # Display messages
    for i, message in enumerate(st.session_state.chat_history):
        if message["type"] == "user":
            # User message
            audio_indicator = ""
            if message.get("is_audio"):
                audio_indicator = '<div class="audio-indicator">🎤 Voice Message</div>'
            
            # Escape user content to prevent HTML injection
            escaped_content = html.escape(message["content"])
            
            st.markdown(f"""
            <div class="user-message">
                {audio_indicator}
                {escaped_content}
                
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # Bot message
            # The bot message can contain newlines, so we replace them with <br> for HTML display
            bot_content_html = message["content"].replace('\n', '<br>')
            st.markdown(f"""
            <div class="bot-message">
                <strong>🌾 AgroAI</strong><br>
                {bot_content_html}
                <div class="message-time">{message["timestamp"]}</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display audio response
            if message.get("audio_bytes"):
                display_audio_player(message["audio_bytes"], f"response_{i}")
            
            # Display sources
            if message.get("sources") and len(message["sources"]) > 0:
                with st.expander("📚 Knowledge Sources", expanded=False):
                    for j, source in enumerate(message["sources"][:3], 1):
                        source_text = str(source)
                        preview = source_text[:200] + "..." if len(source_text) > 200 else source_text
                        
                        st.markdown(f"""
                        <div class="source-card">
                            <div class="source-header">
                                <span>📖</span>
                                <span>Source {j}</span>
                            </div>
                            <div class="source-content">{html.escape(preview)}</div>
                        </div>
                        """, unsafe_allow_html=True)

def process_user_input(user_input, is_audio=False, audio_file_path=None):
    """Process user input with enhanced error handling"""
    # Clean user input to remove any accidental HTML tags
    cleaned_input = re.sub('<[^<]+?>', '', user_input)

    if not cleaned_input.strip():
        st.warning("⚠️ Please enter a question or record audio.")
        return False
    
    try:
        # Add the cleaned user message to chat
        add_message_to_chat("user", cleaned_input, is_audio=is_audio)
        
        # Show typing indicator
        typing_placeholder = st.empty()
        with typing_placeholder.container():
            display_typing_indicator()
        
        # Process the question
        if is_audio and audio_file_path:
            response = st.session_state.assistant.process_audio_question(audio_file_path)
        else:
            # Use the cleaned input for processing
            response = st.session_state.assistant.process_question(cleaned_input)
        
        # Clear typing indicator
        typing_placeholder.empty()
        
        if response and "answer" in response:
            # Add bot response to chat
            add_message_to_chat(
                "bot", 
                response["answer"], 
                audio_bytes=response.get("audio_bytes"),
                sources=response.get("sources", [])
            )
            
            return True
        else:
            st.error("❌ Failed to generate response. Please try again.")
            return False
            
    except Exception as e:
        st.error(f"❌ Error processing your question: {str(e)}")
        st.info("💡 Please check your connection and try again.")
        return False
    
    finally:
        # Clean up temporary file if it exists
        if audio_file_path and os.path.exists(audio_file_path):
            try:
                os.unlink(audio_file_path)
            except:
                pass

def main():
    """Main application with ChatGPT-like interface"""
    initialize_session_state()
    
    # Header
    st.markdown("""
    <div class="header-container">
        <div class="header-title">🌱 AgroAI</div>
        <div class="header-subtitle">Your Intelligent Agricultural Assistant</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if assistant is ready
    if not st.session_state.assistant_ready:
        st.info("⚙️ Initializing AgroAI Assistant...")
        if load_assistant():
            st.success("✅ AgroAI is ready to help you!")
            time.sleep(1)
            st.rerun()
        else:
            st.stop()
    
    # Main layout
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Chat area
        chat_container = st.container()
        with chat_container:
            st.markdown('<div class="chat-container">', unsafe_allow_html=True)
            display_chat_history()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # ChatGPT-like input area
        input_container = st.container()
        with input_container:
            # Recording status
            if st.session_state.recording:
                st.markdown("""
                <div class="recording-status">
                    🔴 Recording... Click the microphone again to stop
                </div>
                """, unsafe_allow_html=True)
            
            # Input form
            with st.form("chat_form", clear_on_submit=True):
                col_input, col_voice, col_send = st.columns([6, 1, 1])
                
                with col_input:
                    user_text = st.text_input(
                        "Message AgroAI...",
                        placeholder="Ask about farming, crops, pests, fertilizers...",
                        label_visibility="collapsed",
                        key="main_input"
                    )
                
                with col_voice:
                    # Voice button
                    if st.session_state.recording:
                        voice_clicked = st.form_submit_button("🔴", help="Stop Recording")
                    else:
                        voice_clicked = st.form_submit_button("🎤", help="Start Voice Recording")
                
                with col_send:
                    send_clicked = st.form_submit_button("➤", help="Send Message")
                
                # Handle voice recording
                if voice_clicked:
                    if st.session_state.recording:
                        # Stop recording
                        st.session_state.recording = False
                        
                        # Create recorder and get audio
                        recorder = AudioRecorder()
                        if hasattr(st.session_state, 'audio_recorder'):
                            audio_bytes = st.session_state.audio_recorder.stop_recording()
                            
                            if audio_bytes:
                                # Create temporary file
                                temp_path = create_temp_audio_file(audio_bytes)
                                
                                if temp_path:
                                    try:
                                        # Transcribe audio
                                        with st.spinner("🔄 Converting speech to text..."):
                                            transcribed_text = st.session_state.assistant.speech_to_text(temp_path)
                                        
                                        if transcribed_text and transcribed_text.strip():
                                            # Process the transcribed question
                                            if process_user_input(transcribed_text, is_audio=True, audio_file_path=temp_path):
                                                st.rerun()
                                        else:
                                            st.error("❌ Could not transcribe audio. Please speak clearly and try again.")
                                    
                                    except Exception as e:
                                        st.error(f"❌ Error processing audio: {str(e)}")
                            else:
                                st.error("❌ No audio recorded. Please try again.")
                        
                        # Clean up
                        if hasattr(st.session_state, 'audio_recorder'):
                            del st.session_state.audio_recorder
                    
                    else:
                        # Start recording
                        recorder = AudioRecorder()
                        if recorder.start_recording():
                            st.session_state.recording = True
                            st.session_state.audio_recorder = recorder
                            st.rerun()
                        else:
                            st.error("❌ Could not start recording. Check microphone permissions.")
                
                # Handle text input
                if send_clicked and user_text:
                    if process_user_input(user_text, is_audio=False):
                        st.rerun()
    
    with col2:
        # Sidebar with stats and controls
        st.markdown("### 📊 Session Stats")
        
        # Calculate stats
        total_questions = len([msg for msg in st.session_state.chat_history if msg["type"] == "user"])
        total_responses = len([msg for msg in st.session_state.chat_history if msg["type"] == "bot"])
        voice_questions = len([msg for msg in st.session_state.chat_history if msg["type"] == "user" and msg.get("is_audio")])
        
        # Display stats
        stats = [
            (total_questions, "Questions"),
            (total_responses, "Responses"), 
            (voice_questions, "Voice Inputs")
        ]
        
        for number, label in stats:
            st.markdown(f"""
            <div class="stat-card">
                <span class="stat-number">{number}</span>
                <div class="stat-label">{label}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Controls
        st.markdown("### ⚙️ Controls")
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            if hasattr(st.session_state.assistant, 'clear_session_memory'):
                st.session_state.assistant.clear_session_memory()
            st.success("✅ Chat cleared!")
            time.sleep(0.5)
            st.rerun()
        
        if st.button("🔄 Restart Assistant", use_container_width=True):
            st.session_state.assistant = None
            st.session_state.assistant_ready = False
            st.session_state.recording = False
            st.info("🔄 Restarting assistant...")
            time.sleep(1)
            st.rerun()
        
        # Export functionality
        if st.session_state.chat_history:
            st.markdown("### 📥 Export")
            
            export_data = []
            for msg in st.session_state.chat_history:
                export_data.append({
                    "timestamp": msg["timestamp"],
                    "type": msg["type"],
                    "content": msg["content"],
                    "is_audio": msg.get("is_audio", False),
                    "source_count": len(msg.get("sources", []))
                })
            
            json_data = json.dumps(export_data, indent=2, ensure_ascii=False)
            
            st.download_button(
                label="📄 Download Chat History",
                data=json_data,
                file_name=f"agroai_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # Quick Help
        st.markdown("### 💡 Quick Help")
        
        with st.expander("🎤 Voice Input Tips"):
            st.markdown("""
            • **Click microphone** to start recording
            • **Speak clearly** and at normal pace
            • **Click again** to stop recording
            • **Quiet environment** works best
            • **Short questions** (10-30 seconds) are ideal
            """)
        
        with st.expander("🌾 Best Questions to Ask"):
            st.markdown("""
            **Crop Management:**
            • "How to grow tomatoes in summer?"
            • "Best fertilizer for wheat crops?"
            • "When to plant rice in Maharashtra?"
            
            **Pest Control:**
            • "How to control aphids naturally?"
            • "Pest management for cotton?"
            • "Organic pesticides for vegetables?"
            
            **Soil & Fertilizers:**
            • "Soil preparation for potato farming"
            • "NPK ratio for maize crops"
            • "Organic compost making process"
            """)
        
        with st.expander("🛠️ Troubleshooting"):
            st.markdown("""
            **Common Issues:**
            
            🔴 **Recording not working:**
            • Check microphone permissions
            • Try refreshing the page
            • Use Chrome/Firefox browser
            
            🔴 **No response generated:**
            • Check internet connection
            • Verify API keys are valid
            • Try rephrasing your question
            
            🔴 **Audio not playing:**
            • Check browser audio settings
            • Try different browser
            • Ensure speakers/headphones work
            """)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.8rem; padding: 1rem;">
            <strong>🌾 AgroAI v2.2</strong><br>
            Powered by Azure OpenAI & GROQ<br>
            <div style="margin-top: 0.5rem;">
                Made with ❤️ for farmers everywhere
            </div>
        </div>
        """, unsafe_allow_html=True)

# Error handling for the main execution
if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"🚨 Critical Error: {str(e)}")
        st.markdown("""
        ### 🛠️ Error Recovery Steps:
        1. **Refresh the page** (F5 or Ctrl+R)
        2. **Check your .env file** has all required keys
        3. **Verify vector database** exists (`faiss_index` folder)
        4. **Run requirements installation**: `pip install -r requirements.txt`
        5. **Check file paths** are correct
        
        If the error persists, check the console for detailed logs.
        """)
        
        # Show detailed error in expander
        with st.expander("🔍 Detailed Error Information"):
            st.code(f"""
Error Type: {type(e).__name__}
Error Message: {str(e)}
            """)
            
            # Show environment status
            st.markdown("**Environment Variables Status:**")
            env_vars = ["AZURE_OPENAI_API_KEY", "ENDPOINT_URL", "AZURE_OPENAI_API_KEY_VB", "AZURE_ENDPOINT_VB", "GROQ_API_KEY"]
            for var in env_vars:
                status = "✅ Set" if os.getenv(var) else "❌ Missing"
                st.write(f"{var}: {status}")
            
            # Show file status
            st.markdown("**File System Status:**")
            files_to_check = ["farm_bot.py", "faiss_index", ".env"]
            for file_path in files_to_check:
                exists = "✅ Exists" if os.path.exists(file_path) else "❌ Missing"
                st.write(f"{file_path}: {exists}")

