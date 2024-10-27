import pandas as pd
import gdown

class DanceMove:
    def __init__(self, name, counts, lesson, grouping):
        self.name = name
        self.counts = counts
        self.lesson = lesson
        self.grouping = grouping

    def __repr__(self):
        return f"DanceMove(name='{self.name}', counts={self.counts}, lesson='{self.lesson}, grouping='{self.grouping}')"


def download_excel_from_gdrive(gdrive_url="https://docs.google.com/spreadsheets/d/1aosvnSmsJQOGKC1ovB38PTfes1ZzHu73/edit?usp=sharing&ouid=111732102481483761509&rtpof=true&sd=true"):
    file_id = gdrive_url.split('/d/')[1].split('/')[0]
    download_url = f'https://drive.google.com/uc?id={file_id}&export=download'

    output_file = 'data_from_gdrive.xlsx'
    gdown.download(download_url, output_file, quiet=False)

    return output_file


class DanceMoveCollection:
    def __init__(self):
        self.moves = []
        self.load_from_excel()

    def load_from_excel(self):
        # file_path = download_excel_from_gdrive()
        file_path = 'data_from_gdrive.xlsx'
        df = pd.read_excel(file_path)

        for index, row in df.iterrows():
            move = DanceMove(
                name=row['Name'],
                counts=row['Counts'],
                lesson=row['Lesson'],
                grouping=row['Grouping']
            )
            self.moves.append(move)

    def get_move_from_name(self, name):
        found_move = [move for move in self.moves if move.name == name]
        if found_move:
            return found_move[0]
        else:
            return None

    def get_grouping_from_name(self, name):
        move = self.get_move_from_name(name)
        if move:
            return move.grouping
        else:
            return None

    def __repr__(self):
        return f"DanceMoveCollection(moves={self.moves})"