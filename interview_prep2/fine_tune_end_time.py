import os
import librosa
import subprocess
import numpy as np
import shutil
import uuid

class AudioManager:
    def __init__(self, video_path, output_folder, start_time=8, gap_of_audio=0.5, ffmpeg_gpu=False, bitrate=4):
        self.video_path = video_path
        self.output_folder = output_folder
        self.audio_folder = os.path.join(self.output_folder, 'audio')
        if not os.path.exists(self.audio_folder):
            os.makedirs(self.audio_folder)
        unique_id = str(uuid.uuid4())
        self.audio_file = os.path.join(self.audio_folder, f"{unique_id}.wav")
        print("self.audio_file ",self.audio_file)
        self.start_time = start_time  
        self.gap_of_audio = gap_of_audio
        self.ffmpeg_gpu = ffmpeg_gpu
        self.stream_bitrate = bitrate
    
    def extract_audio_from_video(self):
        command = [
            'ffmpeg', 
            '-i', self.video_path, 
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ar', '44100', 
            '-ac', '2',  
            self.audio_file  
        ]
        subprocess.run(command, check=True)
        print(f"Audio extracted to {self.audio_file}")
    
    def get_mute_section_array(self, non_mute_array, duration):
        last_v = 0
        mute_array = []
        for non_mute_i in non_mute_array:
            st, et = non_mute_i
            current_mute_st, current_mute_et = last_v, st
            mute_array.append([current_mute_st, current_mute_et])
            last_v = et
        if duration - last_v > 0:
            mute_array.append([last_v, duration])
        return mute_array

    def find_audio_gap(self, non_mute_array, duration, checkFrom=8, gapOfAudio=0.5):
        mute_array = self.get_mute_section_array(non_mute_array, duration)
        matched = 0
        matchFound = False
        if len(mute_array) > 0:
            if mute_array[-1][0] < checkFrom:
                matched = checkFrom
                matchFound = True
            else:
                for mute_s_i in mute_array:
                    st, et = mute_s_i
                    difference = et - st
                    if difference > gapOfAudio and st > checkFrom:
                        matched = st
                        matchFound = True
                        break
        return matchFound, matched

    def find_end_time(self):
        data, sampling_rate = librosa.load(self.audio_file)
        non_silent_sections = librosa.effects.split(data, top_db=20)
        print("Non-silent sections:", non_silent_sections)
        non_silent_time = librosa.samples_to_time(non_silent_sections, sr=sampling_rate)
        end_time_found, end_time = self.find_audio_gap(non_silent_time, len(data) / sampling_rate)
        print(f"End time detected: {end_time} seconds")
        return end_time
        
    def process_video(self):
        self.extract_audio_from_video()
        end_time = self.find_end_time()
        return end_time

def fine_tune(video_path,output_folder):
    print("this is the video_path and the output_folder",video_path,output_folder)
    audio_manager = AudioManager(video_path,output_folder)
    end_time = audio_manager.process_video()
    return end_time