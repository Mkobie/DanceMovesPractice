from pathlib import Path
from DanceMove import DanceMoveCollection


grouping_titles = ["Basic turns", "Ballroom blues", "Ballroom blues - turns", "Close embrace", "Close embrace - spins"]
mixer_moves = {"all": grouping_titles,
               "some": ["Basic turns", "Ballroom blues", "Ballroom blues - turns"],
               "a few": ["Basic turns"]}
bmp_limits = {"min": 30, "max": 300}
mixer_btn_names = {"start": "Let's go!", "stop": "Aaand stop!"}

default_interval = {"bpm": 75}
default_interval["ms"] = 60000 / default_interval["bpm"]

show_video_dropdown_options = ["without video", "with video"]


assets_folder = Path.cwd() / 'assets'
metronome_audio = "/assets/Perc_MetronomeQuartz_hi.wav"

dance_moves = DanceMoveCollection()
