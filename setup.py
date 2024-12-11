from backend.DanceMove import DanceMoveCollection

grouping_titles = ["Basic turns", "Ballroom blues", "Ballroom blues - turns", "Close embrace", "Close embrace - spins"]
mixer_moves = {"all": grouping_titles,
               "some": ["Basic turns", "Ballroom blues", "Ballroom blues - turns"],
               "a few": ["Basic turns"]}
bmp_limits = {"min": 30, "max": 300}
mixer_btn_names = {"start": "Let's go!", "stop": "Aaand stop!"}

default_interval = {"bpm": 75}
default_interval["ms"] = 60000 / default_interval["bpm"]
initial_interval = default_interval["ms"] * 4  # Start with 4 counts of nothing

show_video_dropdown = {False: "without video", True: "with video"}


assets_folder = 'assets'
metronome_audio = "assets/Perc_MetronomeQuartz_hi.wav"

dance_moves = DanceMoveCollection('../data_from_gdrive.xlsx')
dance_moves.set_group_selected_state(dance_moves.groups[0])
