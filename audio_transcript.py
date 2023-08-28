import json, csv
from mp3_to_text import audio_to_transcript
from download_audio_files import download_files
import os, time
import boto3
from dotenv import load_dotenv

load_dotenv()


session = boto3.Session(
aws_access_key_id= os.getenv('ACCESS_KEY'),
aws_secret_access_key=os.getenv('SECRET_ACCESS_KEY'),
region_name=os.getenv('REGION')
)


def upload_file_to_s3(file_path, bucket_name, object_name=None):
    """
    Uploads a file to an S3 bucket.
    
    :param file_path: The local path to the file you want to upload.
    :param bucket_name: The name of the S3 bucket.
    :param object_name: The object name (key) under which the file will be stored in the bucket.
                        If not provided, the filename of the local file will be used.
    :return: True if the upload was successful, False otherwise.
    """
    s3_client = session.client('s3')   
        
    try:
        print(f"Uploading : {object_name}\n")
        s3_client.upload_file(file_path, bucket_name, object_name)
        print(f"Finished Uploading : {object_name}\n")
        return True
    except Exception as e:
        print(f"Error uploading file: {e}")
        return False
    


def read_message():
    sqs = session.resource('sqs')
    queue = sqs.get_queue_by_name(QueueName="Mytestqueue")
    messages = queue.receive_messages(MessageAttributeNames=['All'], )
    if messages:
        for message in messages:
            try:
                output = "Message ID: {0} ".format(message.message_id)
                print(output)
                message_body = json.loads(message.body)
                output = "Message: {0} ".format(message_body)
                print(output)
                message.delete()
                return message_body, True
            except:
                error_message = 'Error in message content: {0} \n'.format(message.body)
                message.delete()
                return error_message, False
    else:
        return "None", False
    
        
def create_object_name(text_file_path, podcast_slug, file_name):
    text_file_path = text_file_path.split('/')[1]
    # print(f'file path :{text_file_path}')
    object_name = podcast_slug+'/'+file_name+'/'+text_file_path
    return object_name
    
    
def correct_time_format(time):    
    if time > 60:
        time = format(time/60, '.2f')
    else:
        time = str(time).split('.')[0]
    return time


def fetching_transcript(audio_file):    
    transcript = audio_to_transcript(audio_file)
    text = transcript.get('text')
    segments = transcript.get('segments')
    return text, segments


def saving_transcript(text_file_path, csv_file_path,audio, podcast_slug, file_name):
    text, segments = fetching_transcript(audio)

    with open(text_file_path, 'w+') as file:
        json.dump(text, file)

    object_name_for_text_file = create_object_name(text_file_path, podcast_slug, file_name)
    print(object_name_for_text_file)

    upload_file_to_s3(text_file_path, bucket_name='elasticbeanstalk-us-east-2-025904421312', object_name=object_name_for_text_file)    

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

    with open(csv_file_path, 'w+', newline='') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)
        writer.writerows(segment_list)

    object_name_for_csv_file = create_object_name(csv_file_path, podcast_slug, file_name)
    upload_file_to_s3(csv_file_path, bucket_name='elasticbeanstalk-us-east-2-025904421312', object_name=object_name_for_csv_file)    


def process_file(file, podcast_slug):
    audio_file = "audio/" + file
    file_name = os.path.splitext(file)[0]
    text_file = "transcripts/" + file_name + ".txt"
    text_file_with_time = "csv_transcripts_files/" + file_name + ".csv"
    saving_transcript(text_file, text_file_with_time, audio_file, podcast_slug, file_name)


def main():
    start_script_time = time.time()
    # read msg from sqs
    msg_data, new_msg = read_message()
    if new_msg:
        audio_url = msg_data
        print(f'audio url : {audio_url} \n')    
    
        podcast_slug = download_files(audio_url)

        try:
            command = "mkdir transcripts csv_transcripts_files"
            if not (os.path.exists('transcripts') and os.path.exists('csv_transcripts_files')):
                os.system(command)

            current_directory = os.getcwd()
            folder_path = os.path.join(current_directory, 'audio')
            dir_list = os.listdir(folder_path)

            for file in dir_list:
                process_file(file, podcast_slug)
                
            end_script_time = time.time()
            print(f'total conversion time : {(end_script_time-start_script_time)/60}')
        
        except Exception as e:
            print(f"Error while converting audio file {e}")
        delete_directory = "rm -r transcripts csv_transcripts_files"
        os.system(delete_directory)
    else:
        print("No new msg in the queue")

        

if __name__== "__main__":    
    while 1:
        main()
        time.sleep(2)        


