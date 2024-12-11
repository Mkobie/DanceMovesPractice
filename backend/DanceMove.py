import random
from typing import Union

import gdown
import pandas as pd

class DanceMove:
    def __init__(self, name, counts, lesson, grouping, selected=False):
        self.name = name
        self.counts = counts
        self.lesson = lesson
        self.grouping = grouping
        self.selected = selected

    def __repr__(self):
        return f"DanceMove(name='{self.name}', counts='{self.counts}', lesson='{self.lesson}', grouping='{self.grouping}', selected='{self.selected}')"


def download_excel_from_gdrive(gdrive_url="https://docs.google.com/spreadsheets/d/1aosvnSmsJQOGKC1ovB38PTfes1ZzHu73/edit?usp=sharing&ouid=111732102481483761509&rtpof=true&sd=true"):
    file_id = gdrive_url.split('/d/')[1].split('/')[0]
    download_url = f'https://drive.google.com/uc?id={file_id}&export=download'

    output_file = 'data_from_gdrive.xlsx'
    gdown.download(download_url, output_file, quiet=False)

    return output_file


class DanceMoveCollection:
    def __init__(self, data: Union[pd.DataFrame, str, None]=None):
        """
        Data can be a pandas dataframe, or an excel.
        :param data:
        """
        self.moves = []
        self.groups = []
        self._basic = DanceMove("Basic", 4, None, None)
        self._sequence_count = 16
        self._current_sequence = []

        if type(data) == pd.DataFrame:
            self.load_data(data)
        elif type(data) == str:
            self.load_from_excel(data)
        else:
            self.load_from_excel()

    def load_from_excel(self, file_path=None):
        file_path = file_path or download_excel_from_gdrive()
        df = pd.read_excel(file_path)
        self.load_data(df)

    def load_data(self, data: pd.DataFrame):
        for index, row in data.iterrows():
            move = DanceMove(
                name=row['Name'],
                counts=row['Counts'],
                lesson=row['Lesson'],
                grouping=row['Grouping'],
            )
            self.moves.append(move)
            self.groups = data["Grouping"].unique().tolist()

    def set_move_selected_state(self, selection_list):
        for i, move in enumerate(self.moves):
            move.selected = selection_list[i]

    def set_group_selected_state(self, group, state:str = "selected"):
        """
        State must be "selected" to set the group selection to true. Anything else will deselect the group.
        """
        target_state = state == "selected"

        moves_to_update = [move for move in self.moves if move.grouping == group]
        for move in moves_to_update:
            move.selected = target_state

    def get_list_of_selected_moves(self) -> list[DanceMove]:
        """
        Returns a list of all moves that are selected in the app.
        """
        return [move for move in self.moves if move.selected]

    def get_list_of_selected_move_names(self) -> list[str]:
        """
        Returns a list of the names of all moves that are selected in the app.
        """
        return [move.name for move in self.moves if move.selected]

    def get_selected_moves_true_false_list(self) -> list[bool]:
        moves_true_false_list = [move.selected for move in self.moves]
        return moves_true_false_list

    def get_list_of_selected_group_names(self) -> list[str]:
        """
        Returns a list of the names of all groups that have all their moves selected.
        """
        group_names = self.groups
        for move in self.moves:
            if not move.selected:
                if move.grouping in group_names:
                    group_names.remove(move.grouping)
        return group_names

    def get_selected_groups_true_false_list(self) -> list[bool]:
        group_true_false_list = {group: True for group in self.groups}

        for move in self.moves:
            if not move.selected:
                group_true_false_list[move.grouping] = False
        return list(group_true_false_list.values())

    def select_groups_up_to(self, end_group):
        end_index = self.groups.index(end_group) + 1
        selected_groups = self.groups[:end_index]

        for move in self.moves:
            if move.grouping in selected_groups:
                move.selected = True
            else:
                move.selected = False

    def _generate_sequence(self):
        remaining_counts = self._sequence_count

        while remaining_counts > 0:
            possible_moves = [move for move in self.get_list_of_selected_moves() if move.counts <= remaining_counts]
            chosen_move = random.choice(possible_moves)
            self._current_sequence.append(chosen_move)
            remaining_counts -= chosen_move.counts

        if remaining_counts == 0:
            return self._current_sequence
        else:
            return self._generate_sequence()

    def get_current_move(self):
        if not self._current_sequence:
            self._generate_sequence()
        return self._current_sequence[0]

    def pop_current_move(self):
        if not self._current_sequence:
            self._generate_sequence()
        return self._current_sequence.pop(0)

    def __repr__(self):
        return f"DanceMoveCollection(groups='{self.groups}', moves='{self.moves}')"
