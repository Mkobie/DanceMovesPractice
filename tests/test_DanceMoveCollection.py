import unittest

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
        self.collection = DanceMoveCollection(dance_move_data)
        self.collection.set_move_selected_state([True, False, True, True])


    def test_get_list_of_selected_moves(self):
        selected_moves = self.collection.get_list_of_selected_moves()

        self.assertEqual('Basic outside turn', selected_moves[0].name)
        self.assertEqual('Promenade', selected_moves[1].name)
        self.assertEqual('Lunge', selected_moves[2].name)

    def test_get_list_of_selected_move_names(self):
        selected_moves = self.collection.get_list_of_selected_move_names()

        expected_list = ['Basic outside turn', 'Promenade', 'Lunge']
        self.assertEqual(expected_list, selected_moves)

    def test_get_selected_moves_true_false_list(self):
        selected_moves_true_false = self.collection.get_selected_moves_true_false_list()

        expected_list = [True, False, True, True]
        self.assertEqual(expected_list, selected_moves_true_false)

    def test_get_list_of_selected_groups(self):
        selected_groups = self.collection.get_list_of_selected_group_names()

        expected_list = ['Ballroom blues', 'Close embrace']
        self.assertEqual(expected_list, selected_groups)

    def test_get_selected_groups_true_false_list(self):
        selected_groups_true_false = self.collection.get_selected_groups_true_false_list()

        expected_list = [False, True, True]
        self.assertEqual(expected_list, selected_groups_true_false)

    def test_select_groups_up_to_group(self):
        self.collection.select_groups_up_to('Ballroom blues')

        expected_list = ['Basic outside turn', 'Basic inside turn', 'Promenade']
        self.assertEqual(expected_list, self.collection.get_list_of_selected_move_names())

    def test_set_group_selection(self):
        self.collection.set_group_selected_state('Basic turns', "selected")
        self.collection.set_group_selected_state('Ballroom blues', "deselected")

        expected_list = ['Basic outside turn', 'Basic inside turn', 'Lunge']
        self.assertEqual(expected_list, self.collection.get_list_of_selected_move_names())

    def test_get_current_move_with_dynamic_selection(self):
        new_move = self.collection.get_move()

        list_of_possible_moves = ['Basic outside turn', 'Promenade', 'Lunge']
        self.assertIn(new_move.name, list_of_possible_moves)
        self.assertNotEqual("Basic inside turn", new_move.name)

        self.collection.set_move_selected_state([False, True, False, False])
        new_move = self.collection.get_move()
        self.assertEqual(new_move.name, "Basic inside turn")

    def test_get_item(self):
        for dance_move in self.collection:
            self.assertIn("DanceMove(", str(dance_move))

    def test_len(self):
        self.assertEqual(4, len(self.collection))

    def test_get_list_of_group_names(self):
        group_names = self.collection.get_groups()

        self.assertEqual(['Basic turns', 'Ballroom blues', 'Close embrace'], group_names)


if __name__ == '__main__':
    unittest.main()
