import time
import whisper
import GPUtil


def audio_to_transcript(audio_path):
    model = whisper.load_model("base")
    start = time.time()
    print(f'Starting Conversion file_path: {audio_path},  Time : {start}')
    GPUtil.showUtilization()
    result = model.transcribe(audio_path, word_timestamps=True)
    GPUtil.showUtilization()    
    end = time.time()
    print(f'Finished Conversion file_path: {audio_path}, Time : {end}')
    print(f'Total Time : {(end-start)/60}')
    return result

