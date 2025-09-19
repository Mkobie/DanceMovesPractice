import os
from backend.DanceMove import DanceMoveCollection

mixer_btn_names = {"start": "Let's go!", "stop": "Aaand stop!"}
show_video_dropdown = {False: "without video", True: "with video"}
CUSTOM_MIXER_MOVES_LABEL = "custom"

bpm_limits = {"min": 30, "max": 300}
default_interval = {"bpm": 75}
default_interval["ms"] = 60000 / default_interval["bpm"]

assets_folder = 'assets'
metronome_audio = "assets/Perc_MetronomeQuartz_hi.wav"

EXCEL_PATH = os.environ["DANCE_MOVES_SHEET_URL"]
STYLES = ["Salsa", "Blues"]
CATALOGS = {
    style: DanceMoveCollection.from_excel(EXCEL_PATH, style)
    for style in STYLES
}
DEFAULT_STYLE = STYLES[0]

def get_catalog(style: str) -> DanceMoveCollection:
    return CATALOGS.get(style, CATALOGS[DEFAULT_STYLE])
