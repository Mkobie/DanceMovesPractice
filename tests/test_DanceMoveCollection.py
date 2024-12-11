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

    def test_get_current_move(self):
        new_move = self.collection.get_current_move()

        list_of_possible_moves = ['Basic outside turn', 'Promenade', 'Lunge']
        self.assertIn(new_move.name, list_of_possible_moves)
        self.assertNotEqual("Basic inside turn", new_move.name)

        new_move_again = self.collection.get_current_move()
        self.assertEqual(new_move, new_move_again)

    def test_pop_current_move(self):
        list_of_move_names = []
        expected_count = 16
        accumulated_count = 0

        while accumulated_count < expected_count:
            new_move = self.collection.pop_current_move()
            list_of_move_names.append(new_move.name)
            accumulated_count += new_move.counts

        list_of_possible_moves = ['Basic outside turn', 'Promenade', 'Lunge']

        self.assertEqual(expected_count, accumulated_count)
        self.assertIn(list_of_move_names[0], list_of_possible_moves)
        self.assertNotIn("Basic inside turn", list_of_move_names)

        starting_move_of_next_sequence = self.collection.pop_current_move()
        self.assertIn("DanceMove", str(starting_move_of_next_sequence))


if __name__ == '__main__':
    unittest.main()
