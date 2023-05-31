import os
import openai
import pyttsx3
import simpleaudio as sa
import speech_recognition as sr

# Setup Recognizer
r = sr.Recognizer()
# API Key
openai.api_key = "ENTER_YOUR_API_KEY"

# ----SFX---FUNCTIONS---- #

# Successfully heard the prompt SFX
def heardprompt_sfx():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    sfx_directory = os.path.join(script_directory, "sfx")
    wakewordsfx = "facetime connect.wav"
    wakewordsfx_path = os.path.join(sfx_directory, wakewordsfx)
    wave_obj = sa.WaveObject.from_wave_file(wakewordsfx_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

# Ending SFX
def endprompt_sfx():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    sfx_directory = os.path.join(script_directory, "sfx")
    endprompt = "facetime end.wav"
    endprompt_path = os.path.join(sfx_directory, endprompt)
    wave_obj = sa.WaveObject.from_wave_file(endprompt_path)
    play_obj = wave_obj.play()
    play_obj.wait_done()

# -------x---------x------- #

# Wake word detection
def wake_detection():
    with sr.Microphone() as source:
        try:
            print("Listening...")
            audio = r.listen(source, timeout=5)
            text = r.recognize_google(audio)
            print("You: " + text)

            if "wake up" in text.lower():
                speak("Hello, How may I help you?")
                return "gpt"
        except sr.UnknownValueError:
            print("...")
        except TimeoutError:
            print("Timeout error. Retrying...")
            return wake_detection()
        except sr.RequestError:
            print("Sorry, my speech recognition service is currently unavailable.")
            return ""
        except sr.WaitTimeoutError:
            print("...")
            return ""
        except Exception as e:
            print(f"An error has occured: {e}")
            return ""

# Listen for prompt after saying the wake word
def listen_speech():
    with sr.Microphone() as source:
        try:
            audio = r.listen(source, timeout=5)
            prompt = r.recognize_google(audio)
            prompt = prompt.lower()
            print("You: " + prompt)
            return prompt
        except sr.UnknownValueError:
            print("I couldn't catch that, say the wake word again")
            speak("I couldn't catch that, say the wake word again")
            endprompt_sfx()
        except sr.RequestError:
            print("Speech Recognition error, say the wake word again")
            speak("Speech Recognition error, say the wake word again")
            endprompt_sfx()
            return ""
        except TimeoutError:
            print("Timeout error, say the wake word again")
            speak("Timeout error, say the wake word again")
            endprompt_sfx()
            return ""
        except sr.WaitTimeoutError:
            print("Timeout error, say the wake word again")
            speak("Timeout error, say the wake word again")
            endprompt_sfx()
            return ""

# Asking chatgpt through voice prompt
def ask_gpt(prompt):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=0.3,
            max_tokens=100
        )
        return response.choices[0].text.strip()
    
    except openai.error.RateLimitError:
        print("Rate Limited! Ask after one minute.")
        speak("Rate Limited! Ask after one minute.")
        endprompt_sfx()
        return ""
    except openai.error.OpenAIError as e:
        print("OpenAI API error:", e)
        return ""
    except Exception as e:
        print("An error has occurred: ", e)
        speak("An error has occurred")
        return ""

# Initialize the engine and voice properties
engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)
# Function for speaking (tts)
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Put all of the functions together
def main():
    with sr.Microphone() as source:
        print("Silence please, calibrating background noise")
        r.adjust_for_ambient_noise(source, duration=2)
        r.energy_threshold = 3000
        print("Calibrated, now speak...")

    while True:
        wake_word = wake_detection()

        if wake_word == "gpt":
            prompt = listen_speech()
            if prompt:
                heardprompt_sfx()
                response = ask_gpt(prompt)
                print("Response: " + response)
                speak(response)
                endprompt_sfx()

if __name__ == "__main__":
    main()
