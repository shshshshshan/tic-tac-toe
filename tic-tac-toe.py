# Import Python's Random API
import random as rand

# Import Python's Time API
import time

# Setting up player's symbols
player_dict = {1: 'X', 2: 'O'}

# Setting up the board
board = [' ' for i in range(9)]
guide_board = [i + 1 for i in range(9)]

# Function for printing the dashboard
def print_dashboard():
    message = 'Let\'s play'
    game = 'Tic-Tac-Toe!'

    print('-' * (len(message) + len(game)) * 2)
    print(f'{message} {game}'.center((len(message) + len(game)) * 2))
    print('-' * (len(message) + len(game)) * 2)

    del message, game
    return

# Function that prompts the user if they want to play with a computer or another player
def play_with_computer():
    print('[C]omputer\n[P]layer')
    c: str = input('Input: ').upper()[0]

    if c == 'C':
        return True
    elif c == 'P':
        return False
    else:
        return play_with_computer()

# Function that prompts the user for player precedence
def first_to_move():
    print('\nDo you want to be the first to move?')
    ftm: str = input('Input (Y/N): ').upper()[0]

    if ftm == 'Y':
        return 1
    elif ftm == 'N':
        return 2
    else:
        return first_to_move() # Dangerous and can cause stack overflow, will fix next time

# Function that updates the board every input
def update_board(board):
    print(f' {board[0]} | {board[1]} | {board[2]} '.center(40))
    print('---+---+---'.center(40))
    print(f' {board[3]} | {board[4]} | {board[5]} '.center(40))
    print('---+---+---'.center(40))
    print(f' {board[6]} | {board[7]} | {board[8]} '.center(40))

# Asking for player moves
def player_move(player):
    print(f'Choose a slot to place mark: {player_dict[player]}')

    try:
        slot = int(input('Input (1-9): ')) - 1

        # Catching invalid inputs
        if slot < 0 or slot >= 9 or board[slot] != ' ':
            raise ValueError

    except ValueError:
        print('\n-- Invalid slot chosen, try again! --\n')
        return player_move(player) # Dangerous and can cause stack overflow

    else:
        board[slot] = player_dict[player]
        del slot

    return

# Random module for bot moves
def bot_move(bot_number):
    """
    The algorithm of this function can be broken down into steps and has 2 parts - Defensive part and Offensive part:

    Defensive mode:

    Firstly, store all of the indexes of the bot's move into a list for use later
    Secondly, we scan the board for all of the opponent's indexes and store them in a list called 'm'.
    We check if the elements of m are one of the winning conditions. If they are, we need to only add the conditions in which the opponent is close to achieving
    We use this list to anticipate the winning move of the opponent and play the winning move of the opponent. In other words, blocking their move

    The other algorithms are for filtering redundant elements and less likely to happen combinations if they're already blocked
    After acquiring the narrowed pool of good moves, we first need to be offensive

    Offensive mode:

    If there is an opportunity that our bot can play to win, grab it
    The process is similar with the defensive mode, the only difference is that the bot scans and creates a list of its own moves that are close to achieving
    a winning combination.
    It will try to check if there is a slot that can complete that winning combination and plays it if there is.

    The bot will check first an opportunity to win which is the 'offensive mode' and then if it can't find that win, it goes 'defensive mode'
    """

    print('Bot is calculating a move')
    bot_moves = [i for i in range(len(board)) if board[i] == player_dict[bot_number]] # Keeping track of all bot moves, i.e. tracking its own moves

    seconds = rand.choice(range((len(bot_moves) + 1))) + 1
    print('Please wait. . .')
    time.sleep(seconds)

    p = [] # P stands for player_pool which tracks and saves the players move coordinates and winning positions
    max_len: int = 0 # This variable's purpose is so that we can prevent storing winning moves that are only of length 1
                     # A case of this is when it first scans a move at index 0, it finds the winning moves that has 0 and there are a lot so we need to only get 1
                     # The purpose of this is so that we can use the length of our pool as a condition later on

    # Getting the max length first
    for combination in win_conditions:
        m = [i for i in combination if board[i] == player_dict[3 - bot_number]] # List of all moves of players that is in the winning combination
        if len(m) > max_len:
            max_len = len(m)

    # Getting only the elements that suffices max_len
    for combination in win_conditions:
        m = [i for i in combination if board[i] == player_dict[3 - bot_number]]
        if len(m) == max_len:
            if m not in p:
                p.append(m)


    # This algorithm filters the player_pool for combinations that is not likely to happen if it's occupied with a bot move
    # Without this, our bot will collect winning combinations even if that combination is already blocked by it because he doesn't see its own moves when finding
    # the opponent's winning combinations
    elems_to_remove = []

    for move in bot_moves:
        for elem in p:
            elem.append(move)
            for combination in win_conditions:
                if sorted(elem) == combination:
                    elems_to_remove.append(elem)
            elem.remove(move)

    for elem in elems_to_remove: # Separated the removing of elements because it causes a bug when removing it while iterating
                                 # There is a case where it skips the other elements since the indexes move when you delete, hence skipping some elements
        if elem in p:
            p.remove(elem)

    del elems_to_remove # Memory handling, we don't need this list anymore 

    pool = [] # Pool here is a pool of winning conditions that the player is close to achieving
    # Implementation of populating our pool list
    for m in p:
        for combination in win_conditions:
            if any(m[i] in combination for i in range(len(m))):
                pool.append(combination)


    narrowed_pool = [] # Narrowed pool is still the pool from before but narrowed down to the closest winning position the player is close to getting
    max_len = 0 # Similarly, only getting the winning position with closer length
    # Implementation of populating narrowed pool
    for i in p:
        for j in pool:
            sim = closest_similarity(i, j)
            if sim > max_len: # This is taking the max length first
                max_len = sim
    for i in p:
        for j in pool:
            sim = closest_similarity(i, j)
            if sim == max_len:
                if j not in narrowed_pool: # This line prevents adding all the previously added lists
                    narrowed_pool.append(j)

    # Debugging tools #

    # print(f'Filtered p: {p}')
    # print("Narrowed: ", narrowed_pool, sep = ' ', end = '\n')
    # print("Bot Moves: ", bot_moves, sep = ' ', end = '\n')

    # Formulating the computer's smarter moves
    # Start of implementing the procedure, the algorithms above are for acquiring the ingredients for our recipe
    bot_winning_moves = []
    max_len: int = 1

    # Offensive mode section
    # Populating our list of bot's winning moves
    for combination in win_conditions:
        m = [i for i in combination if board[i] == player_dict[bot_number]]
        if len(m) > max_len:
            max_len = len(m)

    # Only getting the winning moves of maximum length
    for combination in win_conditions:
        m = [i for i in combination if board[i] == player_dict[bot_number]]
        if len(m) == max_len:
            bot_winning_moves.append(m)

    # This is to catch the case where the bot has no past moves to compare as winning moves, this block will catch the case where it is the bot's first move
    if len(bot_winning_moves) == 0:
        slot = 4 # Slot 4 is the central cell which is considered the best move. If it is available, play it

        if board[slot] != ' ':
            for x in range(9):
                if x % 2 == 0: # This if the central slot is occupied, we go for the corner cells which are the 4 next best options
                    if board[x] == ' ':
                        board[x] = player_dict[bot_number]
                        del bot_winning_moves, p, pool, narrowed_pool
                        return

            for x in range(9):
                if x % 2 == 1: # Testing the non-corner slots since the corner slots are already occupied at this point
                    if board[x] == ' ':
                        board[x] = player_dict[bot_number]
                        del bot_winning_moves, p, pool, narrowed_pool
                        return

        board[slot] = player_dict[bot_number]
        del bot_winning_moves, p, pool, narrowed_pool # Memory handling
        return

    # This algorithm iterates each cells of the board and appends a single imaginary move where if appending it makes our bot win, the bot will play it first before going into defensive mode
    for i in range(9):
        for winning in bot_winning_moves:
            winning.append(i)
            if sorted(winning) in win_conditions:
                slot = i
                if board[slot] == ' ': # This is to catch if the winning move is not blocked by our opponent
                    board[slot] = player_dict[bot_number]
                    del bot_winning_moves, p, pool, narrowed_pool # Memory handling
                    return # Return here prevents our bot from reaching the defensive mode sector which can increase time and memory complexity if not handled
            winning.remove(i)

    del bot_winning_moves # Memory management

    # Defensive moves
    if len(narrowed_pool) != 1: # This is for the case where there is no winning move of the opponent to be blocked
        slot = 4 # Best cell

        adjacents = [ # List of best adjacent moves if opponent moved bad, placed outside because it will be used for the other algorithm(b)
                [0, 1], [6, 3],
                [8, 7], [2, 5]
        ]

        # This is to catch if the opponent played a bad move, the idea is to play a corner adjacent to the non-corner slot the opponent chose
        # This block only works if our bot is first to move and it is its second move
        # Algorithm(a) only works if the opponent played a non-corner slot
        if len(p) == 1 and p[0][0] % 2 == 1: # Algorithm(a)
            for i in range(9):
                if [i, p[0][0]] in adjacents:
                    board[i] = player_dict[bot_number]
                    del p, pool, narrowed_pool, adjacents, bot_moves # Memory management before ending the function
                    return

        # This is for the continuation of finding the best move after opponent made a bad move
        # Algorithm(b) will not execute if the opponent played optimally and if there is a winning move of the opponent to be blocked
        if len(p) == 2: # Algorithm(b)
            adj_cell_chosen = -1 # This is to acquire the previous move of the bot
            target_cell = -1 # This is to acquire the previous move of the opponent
            for i in range(0, 9, 2):
                if i != 4 and i in bot_moves:
                    adj_cell_chosen = i # The previous bot move should be a corner cell
            for x in p:
                for i in range(1, 9, 2):
                    if i in x:
                        target_cell = i # The previous opponent move should be a non-corner cell

            opp = [ # List of best moves after the adjacency move
                [6, [0, 1]], [8, [6, 3]],
                [2, [8, 7]], [0, [2, 5]]
            ]

            for i in range(9): # Finds that best move and plays it, the rest will be taken care of the other algorithms where it finds the finishing move
                if [i, [adj_cell_chosen, target_cell]] in opp:
                    board[i] = player_dict[bot_number]
                    del p, pool, narrowed_pool, adjacents, bot_moves
                    return


        # Algorithm for getting the best moves if opponent played optimally
        if board[slot] != ' ':
            cases = [ # Case where the opponent's play needs a non-corner response, we lose if we play corner
                [1, 3], [5, 7]
            ]

            if len(p) == 2 and sorted([p[0][0], p[1][0]]) in cases or len(bot_moves) > 0:
                diag_move: bool = False
                opponent_moves = [i for i in range(len(board)) if board[i] == player_dict[3 - bot_number]]

                if len(p) != 0: # This block will catch the case where there is an upcoming 2 winnable combination from our opponent
                    best_moves = []
                    for i in opponent_moves:
                        if i % 2 == 1:
                            for pool in narrowed_pool:
                                if i in pool:
                                    best_moves.append(pool)

                    moves = []
                    for lst in best_moves:
                        for elem in lst:
                            moves.append(elem)

                    while len(moves) != 0:
                        slot = rand.choice(moves)

                        if slot % 2 == 0 and board[slot] == ' ':
                            board[slot] = player_dict[bot_number]
                            del p, pool, narrowed_pool, moves, best_moves
                            return

                for x in opponent_moves:
                    if x in range(1, 9, 2):
                        diag_move = True

                if diag_move:

                    for x in range(9):
                        if x % 2 == 0: # Same logic as before, corner cells
                            if board[x] == ' ':
                                board[x] = player_dict[bot_number]
                                del p, pool, narrowed_pool # Memory handling
                                return

            for x in range(9):
                if x % 2 == 1: # Testing all non-corner since all corner cells are occupied at this point
                    if board[x] == ' ':
                        board[x] = player_dict[bot_number]
                        del p, pool, narrowed_pool
                        return

        board[slot] = player_dict[bot_number]
        del p, pool, narrowed_pool # Memory management
        return

    # Below is for the case where there is a winning move of our opponent to be blocked, the first sector above was for taking advantage of the wrong moves of our opponent if they didn't play optimally

    # Rest of the code in this function from here could be refactored but it's left as is for now

    good_pool = rand.choice(narrowed_pool) # Chooses either of the opponents almost winning combination to be blocked
    good_moves = [] # Chooses either cell of the opponent to use, this is for the case where there are 2 cells to be blocked if the opponent has only 1 cell of a winning combination
    # print(f'Good pool: {good_pool}')

    # Populating our good_moves list
    for move in p:
        for elem in good_pool:
            if elem not in move:
                good_moves.append(elem)

    # print(f'Good moves: {list(set(good_moves))}')
    slot = rand.choice(list(set(good_moves))) # Choosing any of the cells that can block the opponent's winning combination

    while board[slot] != ' ':
        slot = rand.choice(list(set(good_moves)))# This is if the cell chosen was already blocked, just in case

    board[slot] = player_dict[bot_number]

    del p, pool, narrowed_pool, good_pool, good_moves # Good programmer :)
    return

# Function for checking if someone has won the game
def check_winner(player):
    for combination in win_conditions:
        if all(board[i] == player_dict[player] for i in combination):
            print(f'\n-- Player {player} wins! --\n')
            return True
    return False

# For checking if there is no winner
def check_tie():
    if ' ' not in board:
        print('\n-- It\'s a tie! --\n')
        return True
    return False

# Listing the winning conditions
win_conditions = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], # Rows
    [0, 3, 6], [1, 4, 7], [2, 5, 8], # Columns
    [0, 4, 8], [2, 4, 6] # Diagonals
]

# Helper functions
def closest_similarity(list1, list2):
    similar_elems: int = 0

    for elem in list1:
        if elem in list2:
            similar_elems += 1

    return similar_elems

# Main driver method
def main():

    # Welcome message
    print_dashboard()

    # Enemy options
    print('\nWho do you want to play with?')
    c = play_with_computer()

    if c:
        ftm = first_to_move()

    # Initial board image
    print()
    update_board(guide_board)
    print()

    # Game loop
    while True:
        # Player 1 move prompt
        if not c:
            player_move(1)
        else:
            if ftm == 1:
                player_move(ftm)
            elif ftm == 2:
                bot_move(3 - ftm)
        print()
        print('-' * 40)
        print()

        # Update after every move
        update_board(board)
        print()

        # Checking for ties and winners
        if check_winner(1) or check_tie():
            break

        # Player 2 move prompt
        if not c:
            player_move(2)
        else:
            if ftm == 1:
                bot_move(3 - ftm)
            elif ftm == 2:
                player_move(ftm)
        print()
        print('-' * 40)
        print()

        # Update after every move
        update_board(board)
        print()

        # Checking for ties and winners
        if check_winner(2) or check_tie():
            break

main()
