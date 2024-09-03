import google.generativeai as genai
import nltk.data
import asyncio
import edge_tts
from pexelsapi.pexels import Pexels
import requests
from nltk.tokenize import TreebankWordTokenizer
import librosa

# Load in APIs
f = open("gemeni_api_key.txt", "r")
gemeni_API = f.read()
genai.configure(api_key=gemeni_API)
global gemeni
gemeni = genai.GenerativeModel("gemini-1.5-flash") # this is the gemeni api object.
f.close()

f = open("pexel_api_key.txt", "r")
pexel_API = f.read()
global pexel
pexel = Pexels(pexel_API) # this is the pexels api object.
f.close()

# get the length of an audio file.
def getAudioLen(filename: str):
    # Load the audio file
    y, sr = librosa.load(f"{filename}.mp3") 

    # Get the duration in seconds
    duration = librosa.get_duration(y=y, sr=sr)
    return duration

# get a summary from google gemeni.
def summarize(input_query: str):
    # query model
    prompt = f"If you were to search for videos to capture the contents of the following sentence: '{input_query}', what would you enter in the search bar?"
    response = gemeni.generate_content(prompt)

    # filter output so it's just english words
    tokenizer = TreebankWordTokenizer()
    tokenized = tokenizer.tokenize(response.text)
    output_query = " ".join(tokenized)

    # return response
    return output_query

# generate script using google gemeni.
def scriptGen(topic: str):
    # query model
    prompt = f"Please briefly explain {topic} in 3 to 5 sentences. Make it highly engaging and interesting, and please keep everything PG."
    response = gemeni.generate_content(prompt)

    # return response
    return response.text

# split script by sentence.
def splitSentence(text: str):
    tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    return tokenizer.tokenize(text)

# text to speech.
def tts(script: str, filename: str):
    VOICES = ['en-US-GuyNeural', 'en-US-JennyNeural']
    VOICE = VOICES[0]
    OUTPUT_FILE = f"{filename}.mp3"

    async def amain():
        communicate = edge_tts.Communicate(script, VOICE)
        await communicate.save(OUTPUT_FILE)

    asyncio.run(amain())

# download mp4 function
def download_mp4(url, save_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url, stream=True)
        
        # Check if the request was successful
        if response.status_code == 200:
            # Open a file in write-binary mode and write the content
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file.write(chunk)
            # print(f"Download complete: {save_path}")
        else:
            print(f"Failed to download file. Status code: {response.status_code}")
    
    except Exception as e:
        print(f"An error occurred: {e}")

# get a stock footage video for any search query.
def getVideo(query_: str,filename: str,minDur:float):
    # search for video
    search_videos = pexel.search_videos(query=query_, orientation='portrait', size='', color='', locale='', page=1, per_page=15)
    i = 0
    while search_videos["videos"][i]["duration"] < minDur:
        i += 1
    video_id = search_videos["videos"][i]["id"]
    download_url = f"https://www.pexels.com/download/video/{video_id}/"

    # download video
    download_mp4(download_url,f"{filename}.mp4")

