import json, csv
from mp3_to_text import audio_to_transcript
import os

def correct_time_format(time):    
    if time > 60:
        # time = time/60
        time = format(time/60, '.2f')
    else:
        time = str(time).split('.')[0]
    return time

def fetching_transcript(audio_file):    
    transcript = audio_to_transcript(audio_file)
    text = transcript.get('text')
    segments = transcript.get('segments')
    return text, segments

def saving_transcript(text_file_path, csv_file_path,audio):
    text, segments = fetching_transcript(audio)

    with open(text_file_path, 'a') as file:
        json.dump(text+'\n', file)    

    header = ['sentence', 'start_time', 'end_time']
    segment_list=[]

    for segment in segments:
        sentence = segment.get('text').strip()
        start = correct_time_format(segment.get('start'))
        end = correct_time_format(segment.get('end'))
        data=[sentence, start,end]
        segment_list.append(data)
        # print(f"sentence: '{segment.get('text')}' | start: '{start}' | end: '{end}'")
    
    # print(segment_list)

    with open(csv_file_path, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(segment_list)

if __name__== "__main__":

    current_directory = os.getcwd()
    folder_path = os.path.join(current_directory, 'audio')
    dir_list = os.listdir(folder_path)
    print(dir_list)
    for file in dir_list:
        audio_file = "audio/"+file
        saving_transcript("text_file.txt", "csv_text_file.csv",audio_file)

    # saving_transcript("text_file.txt", "csv_text_file.csv","audio1.mp3")


