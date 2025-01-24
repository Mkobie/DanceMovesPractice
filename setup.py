from backend.DanceMove import DanceMoveCollection

mixer_btn_names = {"start": "Let's go!", "stop": "Aaand stop!"}
show_video_dropdown = {False: "without video", True: "with video"}

bmp_limits = {"min": 30, "max": 300}
default_interval = {"bpm": 75}
default_interval["ms"] = 60000 / default_interval["bpm"]

assets_folder = 'assets'
metronome_audio = "assets/Perc_MetronomeQuartz_hi.wav"

dance_moves = DanceMoveCollection()
dance_moves.set_group_selected_state(dance_moves.groups[0])
