import random

def generate_dance_sequence(available_moves, total_counts=16):
    sequence = []
    remaining_counts = total_counts

    while remaining_counts > 0:
        possible_moves = [move for move in available_moves if move.counts <= remaining_counts]

        chosen_move = random.choice(possible_moves)
        sequence.append(chosen_move.name)

        remaining_counts -= chosen_move.counts

    if remaining_counts == 0:
        return sequence
    else:
        return generate_dance_sequence(available_moves, total_counts)
