import sounddevice as sd
import numpy as np
import wave
import os
from utils import resource_path

def record_audio(filename=None, duration=5, samplerate=16000):
    if filename is None:
        filename = resource_path("audio/recording.wav")

    audio_dir = os.path.dirname(filename)
    os.makedirs(audio_dir, exist_ok=True)

    print("Recording...")
    audio = sd.rec(int(duration * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()

    with wave.open(filename, 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(samplerate)
        wf.writeframes(audio.tobytes())
        
    print("Saved:", filename)



class AudioRecorder:
    def __init__(self, samplerate=16000):
        self.samplerate = samplerate
        self.channels = 1
        self.frames = []
        self.stream = None
        self.filename = resource_path("audio/recording.wav")

        audio_dir = os.path.dirname(self.filename)
        os.makedirs(audio_dir, exist_ok=True)

    def _callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.frames.append(indata.copy())

    def start(self):
        self.frames = []
        self.stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=self.channels,
            dtype='int16',
            callback=self._callback
        )
        self.stream.start()
        print("Recording started...")

    def stop(self):
        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None
            print("Recording stopped, saving...")

            audio_data = np.concatenate(self.frames, axis=0)

            with wave.open(self.filename, 'w') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.samplerate)
                wf.writeframes(audio_data.tobytes())

            print("Saved:", self.filename)
