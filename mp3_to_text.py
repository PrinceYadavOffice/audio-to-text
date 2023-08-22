import time
import whisper
import GPUtil
import logging

def audio_to_transcript(audio_path):
    model = whisper.load_model("base")
    start = time.time()
    logging.info(f'Starting Conversion ..... Time : {start}')
    GPUtil.showUtilization()
    result = model.transcribe(audio_path, word_timestamps=True)
    GPUtil.showUtilization()    
    end = time.time()
    logging.info(f'Finished Conversion ..... Time : {end}')
    logging.info(f'Total Time : {(end-start)/60}')
    return result

