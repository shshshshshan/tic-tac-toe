# Import block
import os
import time
import random
from typing import Tuple

# Setting up player's symbols
player_dict: dict[int, str] = {1: 'X', 2: 'O'}

# Setting up the board
board: list[str] = [' ' for _ in range(9)]
guide_board: list[int] = [i + 1 for i in range(9)]

# Listing the winning conditions
win_conditions: list[list[int]] = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columns
    [0, 4, 8], [2, 4, 6] # Diagonals
]

def print_dashboard() -> None:
    message: str = 'Let\'s play'
    game: str = 'Tic-Tac-Toe!'

    print('-' * (len(message) + len(game)) * 2)
    print(f'{message} {game}'.center((len(message) + len(game)) * 2))
    print('-' * (len(message) + len(game)) * 2)

    return

def update_board(board: list) -> None:
    print(f' {board[0]} | {board[1]} | {board[2]} '.center(40))
    print('---+---+---'.center(40))
    print(f' {board[3]} | {board[4]} | {board[5]} '.center(40))
    print('---+---+---'.center(40))
    print(f' {board[6]} | {board[7]} | {board[8]} '.center(40))

def pull_up_guide_board() -> None:
    global guide_board
    print()
    update_board(guide_board)
    print()

def check_winner(board: list[str], player: int) -> bool:
    for combination in win_conditions:
        if all(board[i] == player_dict[player] for i in combination):
            return True
    return False

def check_tie(board: list[str]) -> bool:
    return ' ' not in board

def minimaxMove(board: list[str], maxPlayer: int, maxDepth: int) -> int:
    moves = minimax(board, maxPlayer, 3 - maxPlayer, 1, maxDepth)
    viable_moves = [move for move, score in moves[1].items() if score == moves[0]]
    # print(moves)
    # print(viable_moves)
    return random.choice(viable_moves)

def minimax(board: list[str], maxPlayer: int, minPlayer: int, depth: int, maxDepth: int, alpha: int = float('-inf'), beta: int = float('inf')) -> Tuple[int, dict[int, int]]:

    # print(f'Depth: {depth}')
    if depth == maxDepth or endState(board):
        # print(f'Engine stop, winner = { { 1 : f"Player {player_dict[maxPlayer]}", -1 : f"Player {player_dict[3 - maxPlayer]}", 0 : "Tie"}[points(board, maxPlayer)] }')
        return points(board, maxPlayer) * (maxDepth - depth), None

    currentPlayer = turn(board)

    if currentPlayer == maxPlayer:
        best_score: int = float('-inf')
        legal_moves: list[int] = get_legal_moves(board)
        best_moves: dict[int, int] = {}
        # print(f'Max player\'s turn: {legal_moves}')

        for move in legal_moves:
            future_board = future(board, move, maxPlayer)
            score, _ = minimax(future_board, maxPlayer, minPlayer, depth + 1, maxDepth, alpha, beta)

            if score >= best_score:
                best_score = score
                best_moves[move] = score

            alpha = max(alpha, best_score)

            if alpha > beta:
                break

        return best_score, best_moves

    if currentPlayer == minPlayer:
        best_score: int = float('inf')
        legal_moves: list[int] = get_legal_moves(board)
        best_moves: dict[int, int] = {}
        # print(f'Min player\'s turn: {legal_moves}')

        for move in legal_moves:
            future_board = future(board, move, minPlayer)
            score, _ = minimax(future_board, maxPlayer, minPlayer, depth + 1, maxDepth, alpha, beta)

            if score <= best_score:
                best_score = score
                best_moves[move] = score

            beta = min(beta, score)
            if alpha > beta:
                break

        return best_score, best_moves

    return 0, None

def points(board: list[str], player: int) -> int:
    if check_winner(board, player):
        return 1
    elif check_winner(board, 3 - player):
        return -1
    else:
        return 0

def endState(board: list[str]) -> bool:
    return check_winner(board, 1) or check_winner(board, 2) or check_tie(board)

def turn(board: list[str]) -> int:
    return 1 if len([symbol for symbol in board if symbol == ' ']) % 2 == 1 else 2

def get_legal_moves(board: list[str]) -> list[int]:
    return [move for move in range(9) if board[move] == ' ']

def future(board: list[str], move: int, player: int) -> list[str]:
    copyboard = [symbol for symbol in board]
    copyboard[move] = player_dict[player]
    # update_board(copyboard)
    return copyboard

def human_move(symbol: int) -> None:
    slot = None
    guide_board_active = False
    warned = False

    global board
    while slot == None:
        try:
            print()
            print('-' * 40)
            print(f'Choose a slot to place mark: {player_dict[symbol]}')
            slot = input('Input (1-9): ')

            # Board pull up
            if slot.strip().lower() == 'b':
                slot = None
                os.system('cls')
                update_board(board)
                continue
            elif not guide_board_active and slot.strip().lower() == 'g':
                slot = None
                guide_board_active = True
                pull_up_guide_board()
                continue
            elif guide_board_active and not warned and slot.strip().lower() == 'g':
                slot = None
                warned = True
                print('\n-- Guide board already active --\n')
                continue
            elif slot == '':
                slot = None
                continue
            else:
                slot = int(slot) - 1
                if slot < 0 or slot >= 9 or board[slot] != ' ':
                    slot = None
                    raise ValueError

        except ValueError:
            slot = None
            print('\n-- Invalid slot chosen, try again! --\n')

    else:
        board[slot] = player_dict[symbol]

    return None

def bot_move(symbol: int, difficulty: int) -> None:
   print(f'Bot is calculating a move. . .')
   global board
   move = minimaxMove(board, symbol, difficulty)
   time.sleep(1)
   board[move] = player_dict[symbol]
   return None

def difficulty_selection() -> int:
    print('\n-- Choose a difficulty --\n')
    print('[1] Easy', '[2] Medium', '[3] Hard', sep='\n', end='\n\n')

    choice = None

    while not choice:
        try:
            choice = int(input('Choice: '))

            if choice not in range(1, 4):
                choice = None
                print('\nChoice is not in range!\n')

        except ValueError:
            choice = None
            print('\nPlease input a valid number\n')

    return {1 : 3, 2 : 5, 3 : 10}[choice] # Values inside dictionary are maximum depth

def playwithwho() -> str:
    print('\n-- Please select a game mode --\n')
    print('[1] Player vs Player', '[2] Player vs Computer', '[3] Computer vs Computer', sep='\n', end='\n')

    choice = None

    while not choice:
        try:
            choice = int(input('Choice: '))

            if choice not in range(1, 4):
                choice = None
                print('\nChoice is not in range!\n')

        except ValueError:
            choice = None
            print('\nPlease input a valid number\n')

    return {1 : 'Human', 2 : 'Computer', 3 : 'Entertainment'}[choice]

def symbol_choice() -> int:
    print('\n-- Who would you like to play as? --\n')
    print('[1] Player X', '[2] Player O', sep='\n', end='\n')

    choice = None

    while not choice:
        try:
            choice = int(input('Choice: '))

            if choice not in range(1, 3):
                choice = None
                print('\nChoice is not in range!\n')

        except ValueError:
            choice = None
            print('\nPlease input a valid number\n')

    return choice


# Main method
def main() -> None:
    global board
    global guide_board
    
    # Welcome message
    print_dashboard()

    pvp: str = playwithwho()
    player: int = 1
    bot: int = -1
    difficulty: int = -1
    main_player: str = player_dict[1]

    if pvp == 'Computer':
        player = symbol_choice()
        bot = 3 - player
        difficulty = difficulty_selection()
    elif pvp == 'Human':
        player = symbol_choice()
    elif pvp == 'Entertainment':
        difficulty = difficulty_selection()

    os.system('cls')

    # Initial board image
    print('-- This board is your guide on which cell to input --\n')
    update_board(guide_board)
    print()

    print('-- Press ENTER When You\'re Ready --')
    input()

    os.system('cls')
    update_board(board)
    print()

    # Game loop
    while not endState(board):

        if pvp == 'Entertainment':
            bot_move(player, difficulty)
            player = 3 - player

        elif pvp == 'Human':
            print(f'\n-- Player {1 if player_dict[player] == main_player else 2} to move --')
            human_move(player)
            player = 3 - player

        elif pvp == 'Computer':
            if main_player == player_dict[player]:
                human_move(player)
                main_player = player_dict[3 - player]
            else:
                bot_move(bot, difficulty)
                main_player = player_dict[3 - bot]

        os.system('cls')

        # Update after every move
        update_board(board)
        print()


    winner = { 1 : 'You win!', -1 : 'Opponent wins!', 0 : 'It\'s a tie!' }[points(board, player)]
    print(f'{winner}')

# Script invocation guard
if __name__ == '__main__':
    main()
