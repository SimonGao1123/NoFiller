import pyaudio
import json
from vosk import Model, KaldiRecognizer

# Load the model (path to the unzipped folder)
model = Model("vosk-model-small-en-us-0.15")
recognizer = KaldiRecognizer(model, 16000)

# Set up microphone stream
mic = pyaudio.PyAudio()
stream = mic.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=2048
)
stream.start_stream()

print("Listening... (say something, Ctrl+C to stop)")

i = 0
trigger_word_count = 0

try:
    while True:
        data = stream.read(2048, exception_on_overflow=False)

        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get("text", "")
            if text:
                print("Final:", text)
            trigger_word_count += i
            i = 0
        
        else:
            partial = json.loads(recognizer.PartialResult())

            partial_text = partial.get("partial", "")
            if partial_text:
                print("Partial:", partial_text, end="\r")

            word = "like"
            current_count = partial_text.split().count(word)

            # if there are MORE "like"s now than we've already triggered on
            while current_count > i:
                i += 1
                print(f" --STOP-- don't say: {word}, counter: {i}")


except KeyboardInterrupt:
    print(f"\nStopped. Total triggered words: {trigger_word_count}")
    stream.stop_stream()
    stream.close()
    mic.terminate()