import os
import requests
import concurrent.futures
from urllib.parse import urlparse



def extract_filename_from_s3_url(s3_url):
    parsed_url = urlparse(s3_url)
    path = parsed_url.path
    # The filename will be the last part of the path after the last slash '/'
    filename = path.split('/')[-1]
    return filename

def download_audio_from_api(api_url):
    save_path = "audio/"+extract_filename_from_s3_url(api_url)
    if os.path.exists(save_path):
        print(f"File already exists: {save_path}. Skipping download.")
        return
    
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        print(f"starting Downloadin audio file{api_url}")
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"Audio file downloaded: {save_path}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to download audio from {api_url}: {e}")


def fetch_data_from_api(api_url):
    try:
        response = requests.get(api_url)
        response.raise_for_status()  # Raise an exception for 4xx and 5xx status codes
        data = response.json()  # Assuming the API returns JSON data
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching data: {e}")
        return None
    

def download_audio_files_parallel(urls, max_workers=5):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(download_audio_from_api, url): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error occurred while downloading audio from {url}: {e}")

# Example usage

def download_files(audio_url):
    try:
        # api_url = "https://harkaudio.com/api/v0/external/getPodcastBySlug?podcast=waveform-the-mkbhd-podcast-vox-media-podcast-network"
        api_url = audio_url
        data = fetch_data_from_api(api_url)    
        audio_files=[]
        total_duration = 0
        create_adio_dir = 'mkdir audio'
        os.system(create_adio_dir)
        if data:
            podcasts = data['podcasts']
            podacast_slug = data['podcastSlug']
            for podcast in podcasts:
                total_duration += podcast.get('duration')
                audio_url = podcast.get('s3audioUrl')
                if total_duration <= 15000:
                    audio_files.append(audio_url)
        print(f"{len(audio_files)}")
        download_audio_files_parallel(audio_files)
        return podacast_slug
    except Exception as e:
        print(f"Error while downloading audio files {e}")

# download_files()