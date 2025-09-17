import tempfile
import unittest
from pathlib import Path

import pandas as pd

from backend.DanceMove import DanceMoveCollection


class TestDanceMoveCollection(unittest.TestCase):
    def setUp(self):
        dance_move_data = pd.DataFrame({
            'Name': ['Basic outside turn', 'Basic inside turn', 'Promenade', 'Lunge'],
            'Counts': [8, 8, 4, 4],
            'Lesson': [None, None, None, None],
            'Grouping': ['Basic turns', 'Basic turns', 'Ballroom blues', 'Close embrace'],
        })
        dance_move_data.name = "Blues"
        self.collection = DanceMoveCollection(dance_move_data)
        self.collection._set_move_selected_state([True, False, True, True])

    def test_get_item(self):
        for dance_move in self.collection:
            self.assertIn("DanceMove(", str(dance_move))

    def test_len(self):
        self.assertEqual(4, len(self.collection))

    def test_get_list_of_group_names(self):
        group_names = self.collection.get_groups()

        self.assertEqual(['Basic turns', 'Ballroom blues', 'Close embrace'], group_names)

    def test_get_style_name(self):
        self.assertEqual("Blues", self.collection.get_style_name())

    def test_load_one_excel_tab(self):
        temp_file = Path(tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx").name)
        with pd.ExcelWriter(temp_file) as writer:
            pd.DataFrame({"Name": ['Basic outside turn', 'Basic inside turn', 'Promenade', 'Lunge'],
                          "Counts": [8, 8, 4, 4],
                          "Lesson": ["lesson_link", "lesson_link", "lesson_link", "lesson_link"],
                          "Grouping": ['Basic turns', 'Basic turns', 'Ballroom blues', 'Close embrace']}).to_excel(
                writer, sheet_name="Blues", index=False)

        collection = DanceMoveCollection(str(temp_file))
        self.assertEqual('Blues', collection.get_style_name())
        temp_file.unlink()


if __name__ == '__main__':
    unittest.main()
