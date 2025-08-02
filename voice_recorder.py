import speech_recognition as sr
import threading
import queue
from datetime import datetime

print("DEBUG: Starting voice_recorder module initialization...")

class VoiceRecorder:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = None
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.text_queue = queue.Queue()
        self.recognition_thread = None
        self.recording_thread = None
        self.initialized = False
        
        # Try to initialize microphone
        try:
            self.microphone = sr.Microphone()
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            self.initialized = True
            print("Voice recorder initialized successfully")
        except Exception as e:
            print(f"Warning: Could not initialize microphone: {e}")
            self.initialized = False
    
    def start_recording(self):
        """Start voice recording"""
        if not self.initialized:
            print("Voice recorder not initialized - microphone not available")
            return False
            
        if not self.is_recording:
            self.is_recording = True
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recognition_thread = threading.Thread(target=self._process_audio)
            self.recording_thread.daemon = True
            self.recognition_thread.daemon = True
            self.recording_thread.start()
            self.recognition_thread.start()
            print("Voice recording started...")
            return True
        return False
    
    def stop_recording(self):
        """Stop voice recording"""
        self.is_recording = False
        if self.recording_thread:
            self.recording_thread.join(timeout=1)
        if self.recognition_thread:
            self.recognition_thread.join(timeout=1)
        print("Voice recording stopped...")
    
    def _record_audio(self):
        """Continuously record audio in chunks"""
        if not self.microphone:
            return
            
        with self.microphone as source:
            while self.is_recording:
                try:
                    # Listen for audio with timeout
                    audio = self.recognizer.listen(source, timeout=1, phrase_time_limit=5)
                    self.audio_queue.put(audio)
                except sr.WaitTimeoutError:
                    pass  # Continue listening
                except Exception as e:
                    print(f"Recording error: {e}")
    
    def _process_audio(self):
        """Process recorded audio and convert to text"""
        while self.is_recording or not self.audio_queue.empty():
            try:
                if not self.audio_queue.empty():
                    audio = self.audio_queue.get(timeout=1)
                    # Convert audio to text
                    text = self.recognizer.recognize_google(audio)
                    if text.strip():
                        self.text_queue.put(text)
                        print(f"Recognized: {text}")
                        # Analyze sentiment and save
                        self._analyze_and_save(text)
            except sr.UnknownValueError:
                pass  # Could not understand audio
            except sr.RequestError as e:
                print(f"Speech recognition error: {e}")
            except queue.Empty:
                pass
            except Exception as e:
                print(f"Processing error: {e}")
    
    def _analyze_and_save(self, text):
        """Analyze sentiment and save to keystrokes file"""
        try:
            # Import analyzer locally to avoid circular import issues
            from analyzer import analyzer, THRESHOLD
            
            # Append to keystrokes file for mood tracking
            with open("keystrokes.txt", "a", encoding="utf-8") as f:
                f.write(text + "\n")
            
            # Get sentiment score
            score = analyzer.polarity_scores(text)['compound']
            timestamp = datetime.now().isoformat()
            
            print(f"Voice sentiment: {score:.3f} ({'NEGATIVE' if score < THRESHOLD else 'POSITIVE'})")
            
        except Exception as e:
            print(f"Analysis error: {e}")
    
    def get_latest_text(self):
        """Get the latest recognized text"""
        texts = []
        while not self.text_queue.empty():
            try:
                texts.append(self.text_queue.get_nowait())
            except queue.Empty:
                break
        return texts

# Global voice recorder instance
try:
    voice_recorder = VoiceRecorder()
except Exception as e:
    print(f"Failed to create voice recorder: {e}")
    # Create a dummy voice recorder for fallback
    class DummyVoiceRecorder:
        def __init__(self):
            self.is_recording = False
            self.initialized = False
        def start_recording(self):
            print("Voice recording not available")
            return False
        def stop_recording(self):
            pass
        def get_latest_text(self):
            return []
    voice_recorder = DummyVoiceRecorder()
