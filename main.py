from external_functions import *
from moviepy.editor import *
import time
import os
import shutil

topic = input("Topic of fact video: ")

# create tmp directories
os.system("mkdir video_files")
os.system("mkdir audio_files")

# generate script for video
print("Generating script...")
script = scriptGen(topic)
print("Script generated.")

# split script into sentences
sentences = splitSentence(script)

print("Generating audio and downloading clips...")
for i, sentence in enumerate(sentences):
    # create TTS mp3 for each sentence
    tts(sentence,f"audio_files\sentence{i}")
    clip_len = getAudioLen(f"audio_files\sentence{i}")
    # summarize sentence
    sentence_summary = summarize(sentence)
    # search summary on pexels, and download most relevant video
    getVideo(sentence_summary,f"video_files\clip{i}",clip_len)
    time.sleep(5)
print("Audio generated and clips downloaded.")

print("Editing the video together...")
clipList = list()
for i, sentence in enumerate(sentences):
    # replace downloaded video to length of audio clip
    clip_len = getAudioLen(f"audio_files\sentence{i}")
    clip = VideoFileClip(f"video_files\clip{i}.mp4") 
    clip = clip.subclip(0, clip_len*1.05)
    # replace audio
    audio_clip = AudioFileClip(f"audio_files\sentence{i}.mp3")
    clip = clip.set_audio(audio_clip)
    # resize clip
    clip = clip.resize((720, 1280))
    clipList.append(clip)
print("Video edited.")
    
# sew all the clips
final_clip = concatenate_videoclips(clipList)

# export video
final_clip.write_videofile(f"{topic}.mp4", codec="libx264", audio_codec="aac")

# delete temp directories
shutil.rmtree("video_files")
shutil.rmtree("audio_files")