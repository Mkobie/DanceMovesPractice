from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Union

import gdown
import pandas as pd

class DanceMove:
    def __init__(self, name, counts, lesson, grouping, move_id, selected=False):
        self.name = name
        self.counts = counts
        self.lesson = lesson
        self.grouping = grouping
        self.move_id = move_id
        self.selected = selected

    def __repr__(self):
        return f"DanceMove(name='{self.name}', counts='{self.counts}', lesson='{self.lesson}', grouping='{self.grouping}', id={self.move_id}, selected='{self.selected}')"

def download_excel_from_gdrive(gdrive_url: str, cache_path: str = "data/catalog.xlsx", force_refresh: bool = False, ttl: timedelta | None = None) -> str:
    cache = Path(cache_path)
    cache.parent.mkdir(parents=True, exist_ok=True)

    if cache.exists() and not force_refresh:
        if ttl is None:
            return str(cache)
        age = datetime.now(timezone.utc) - datetime.fromtimestamp(cache.stat().st_mtime, tz=timezone.utc)
        if age <= ttl:
            return str(cache)

    file_id = gdrive_url.split('/d/')[1].split('/')[0]
    download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
    gdown.download(download_url, str(cache), quiet=False)
    return str(cache)


class DanceMoveCollection:
    def __init__(self, data: Union[pd.DataFrame, str, None]=None):
        """
        Data can be a pandas dataframe, or an excel.
        :param data:
        """
        self._style = None
        self.moves = []
        self.groups = []
        self._basic = DanceMove("Basic", 4, None, None, None)
        self._sequence_count = 16
        self._remaining_counts = self._sequence_count

        if type(data) == pd.DataFrame:
            self.load_data(data)

    def __getitem__(self, index) -> Union[DanceMove, None]:
        if self.moves:
            return self.moves[index]
        else:
            return None

    def __len__(self):
        return len(self.moves)

    @classmethod
    def from_excel(cls, file_path: str, sheet_name: str):
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        df.name = sheet_name
        return cls(df)

    def load_data(self, data: pd.DataFrame):
        self._style = data.name
        for index, row in data.iterrows():
            move = DanceMove(
                name=row['Name'],
                counts=row['Counts'],
                lesson=row["Lesson"] if "Lesson" in data.columns else None,
                move_id=row["ID"],
                grouping=row['Grouping'],
            )
            self.moves.append(move)
            self.groups = data["Grouping"].unique().tolist()

    def _set_move_selected_state(self, selection_list):
        for i, move in enumerate(self.moves):
            move.selected = selection_list[i]

    def get_groups(self):
        return self.groups

    def get_style_name(self):
        return self._style

    def __repr__(self):
        return f"DanceMoveCollection(groups='{self.groups}', moves='{self.moves}')"

    @property
    def sequence_count(self) -> int:
        return self._sequence_count

    @property
    def basic_move(self) -> DanceMove:
        return self._basic

    def counts_map(self) -> dict[str, int]:
        return {m.name: m.counts for m in self.moves}

    def groups_map(self) -> dict[str, list[int]]:
        mp: dict[str, list[int]] = {g: [] for g in self.groups}
        for i, m in enumerate(self.moves):
            mp[m.grouping].append(i)
        return mp
