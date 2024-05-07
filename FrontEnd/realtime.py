import os
import re
import time
import azure.cognitiveservices.speech as speechsdk
from banditTextGen import textGen

keywords = ['Hey, Tiago', 'Hey Tiago', 'Hi, Tiago', 'Hi Tiago', 'Tiago', 'Hey, Bandit', 'Hey Bandit', 'Hi, Bandit', 'Hi Bandit', 'Bandit']
endwords = ['End conversation.', 'That will be all.']
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
#audio config
speaker_device_index = 0  # Change this to the correct index
# Create an AudioOutputConfig with the specified speaker device
audio_config = speechsdk.audio.AudioOutputConfig(device_name=f"plughw:{speaker_device_index},0")
#default voice can be change or custom
speech_config.speech_synthesis_voice_name='en-US-GuyNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)



def conversation_transcriber_recognition_canceled_cb(evt: speechsdk.SessionEventArgs):
    print('Canceled event')

def conversation_transcriber_session_stopped_cb(evt: speechsdk.SessionEventArgs):
    print('SessionStopped event')

def conversation_transcriber_transcribed_cb(evt: speechsdk.SpeechRecognitionEventArgs):
    print('TRANSCRIBED:')
    if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print('\tText={}'.format(evt.result.text))
        print('\tSpeaker ID={}'.format(evt.result.speaker_id))
    elif evt.result.reason == speechsdk.ResultReason.NoMatch:
        print('\tNOMATCH: Speech could not be TRANSCRIBED: {}'.format(evt.result.no_match_details))

def conversation_transcriber_session_started_cb(evt: speechsdk.SessionEventArgs):
    print('SessionStarted event')


def printline(): print('------------------------------------------------\n')


def from_mic():
    # Set the desired device index (replace with your actual device index)
    device_index = 1

    # Create a Microphone instance with the specified device index
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=speechsdk.audio.AudioConfig(device_name=f"plughw:{device_index},0"))

    print("Speak into your microphone.")
 
    while True:
        result = speech_recognizer.recognize_once_async().get()
        transcription = result.text.strip()
        print(transcription)
        
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            print("Recognized: {}".format(transcription))
            
            keyword_detected = False
            endword_detected = any(re.search(re.escape(endword), transcription, re.IGNORECASE) for endword in endwords)
            
            response = None
            for keyword in keywords:
                match = re.search(re.escape(keyword), transcription, re.IGNORECASE)
                if match:
                    print('KeyPhrase detected.')
                    keyword_detected = True
                    # Extract substring from the keyword to the end of the string
                    start_index = match.start()
                    transcription = transcription[start_index:]
                    print(f"This text will be sent to GPT '{transcription}'")
                    printline()
                    response = banditText.textGen(transcription)
                    if response:
                        to_speaker(response)
                    break
            
            if endword_detected:
                print("Ending conversation.")
                break  # Exit the loop if an endword is detected
            
            if not keyword_detected and not endword_detected:
                print('No keywords detected, continue listening.')
                printline()
        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(result.no_match_details))
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")
                break




def to_speaker(text):
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    
    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

try:
    banditText = textGen()
    from_mic()
except Exception as err:
    print("Encountered exception. {}".format(err))
