import time
import whisper

def audio_to_transcript(audio_path):
    model = whisper.load_model("base")
    start = time.time()
    print(f'Starting Conversion ..... Time : {start}')
    result = model.transcribe(audio_path, word_timestamps=True)
    end = time.time()
    print(f'Finished Conversion ..... Time : {end}')
    print(f'Total Time : {(end-start)/60}')
    return result

