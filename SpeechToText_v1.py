import re
import json
import pyaudio
from vosk import Model, KaldiRecognizer

# fillers = ["like", "you know", "basically"]

def count_fillers(text, fillers):
    result = {}
    for f in fillers:
        pattern = rf"\b{re.escape(f)}\b"      # create a regex pattern for the filler word
        matches = re.findall(pattern, text)   # list of every match found
        result[f] = len(matches)              # store how many there were
    return result


def alert_filler(counts, alerted, emit):
    for word, n in counts.items():
        while alerted[word] < n:
            alerted[word] += 1
            emit(f"--STOP-- don't say: {word}, counter: {alerted[word]}")


def finish_phrase(text, alerted, totals, fillers, emit):
    counts = count_fillers(text, fillers)
    alert_filler(counts, alerted, emit)
    # print(alerted)
    # print(totals)
    for w in fillers:
        totals[w] += counts[w]             # totals come from final text only
        alerted[w] = 0                     # reset for the next sentence


def speech(fillers, emit=print, on_partial=None, should_stop=lambda: False):
    model = Model("vosk-model-small-en-us-0.15")
    recognizer = KaldiRecognizer(model, 16000)

    mic = pyaudio.PyAudio()
    stream = mic.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=16000,
        input=True,
        frames_per_buffer=4096,
    )
    stream.start_stream()

    alerted = {f: 0 for f in fillers}
    totals = {f: 0 for f in fillers}

    emit("Listening...")

    #try/except not good code, need to change ltr
    try:
        while not should_stop():
            data = stream.read(2048, exception_on_overflow=False)

            if recognizer.AcceptWaveform(data):
                text = json.loads(recognizer.Result()).get("text", "")
                if text:
                    emit(f"Final: {text}")
                    print(f"Final: {text}")
                finish_phrase(text, alerted, totals, fillers, emit)
            else:
                partial_text = json.loads(recognizer.PartialResult()).get("partial", "")
                if partial_text and on_partial:
                    on_partial(partial_text)
                # print(count_fillers(partial_text))
                alert_filler(count_fillers(partial_text, fillers), alerted, emit)

    except KeyboardInterrupt:
        pass
    finally:
        text = json.loads(recognizer.FinalResult()).get("text", "")
        finish_phrase(text, alerted, totals, fillers, emit)
        emit(f"Stopped. Total fillers: {sum(totals.values())} {totals}")
        print(f"Stopped. Total fillers: {sum(totals.values())} {totals}")
        stream.stop_stream()
        stream.close()
        mic.terminate()

# # speech(fillers)