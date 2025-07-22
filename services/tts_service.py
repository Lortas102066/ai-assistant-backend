from google.cloud import texttospeech
import os

class TTSService:
    def __init__(self):
        # Initialize Google Cloud TTS client
        # Credentials should be set via GOOGLE_APPLICATION_CREDENTIALS env var
        self.client = texttospeech.TextToSpeechClient()
    
    async def synthesize(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech using Google Cloud Text-to-Speech
        """
        try:
            # Set up synthesis input
            synthesis_input = texttospeech.SynthesisInput(text=text)
            
            # Build voice request
            voice = texttospeech.VoiceSelectionParams(
                language_code=self._get_language_code(language),
                ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
            )
            
            # Select audio config
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )
            
            # Perform text-to-speech synthesis
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=audio_config
            )
            
            return response.audio_content
            
        except Exception as e:
            raise Exception(f"TTS synthesis failed: {str(e)}")
    
    def _get_language_code(self, language: str) -> str:
        """Convert simple language code to Google TTS format"""
        language_map = {
            "en": "en-US",
            "ja": "ja-JP",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
            "pt": "pt-BR",
            "ru": "ru-RU",
            "ko": "ko-KR",
            "zh": "zh-CN"
        }
        
        return language_map.get(language, "en-US")