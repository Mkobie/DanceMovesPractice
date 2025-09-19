from backend.DanceMove import DanceMoveCollection

mixer_btn_names = {"start": "Let's go!", "stop": "Aaand stop!"}
show_video_dropdown = {False: "without video", True: "with video"}
CUSTOM_MIXER_MOVES_LABEL = "custom"

bpm_limits = {"min": 30, "max": 300}
default_interval = {"bpm": 75}
default_interval["ms"] = 60000 / default_interval["bpm"]

assets_folder = 'assets'
metronome_audio = "assets/Perc_MetronomeQuartz_hi.wav"

EXCEL_PATH = "https://docs.google.com/spreadsheets/d/1aosvnSmsJQOGKC1ovB38PTfes1ZzHu73/edit?usp=sharing&ouid=111732102481483761509&rtpof=true&sd=true"
STYLES = ["Salsa", "Blues"]
CATALOGS = {
    style: DanceMoveCollection.from_excel(EXCEL_PATH, style)
    for style in STYLES
}
DEFAULT_STYLE = STYLES[0]

def get_catalog(style: str) -> DanceMoveCollection:
    return CATALOGS.get(style, CATALOGS[DEFAULT_STYLE])
