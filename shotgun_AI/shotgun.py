"""
The MIT License (MIT)
Copyright (c) 2015 David Greydanus
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Created on Dec 15, 2013

@author: DavidGrey
"""

import sys
import tty
import termios
import os
from os import _exit
from random import choice
from states import game_states
from ascii_art import (gun_art, shield_art, reload_art,
                       win_art, loss_art, goodbye_art)


CLEAR = "\n" * 50

print game_states
def getch():
    """Waits for a single key input
    and the returns it without need for the enter key
    to be pressed mimicking the behavior of msvcrt.getwch() in
    Windows"""
    file_desc = sys.stdin.fileno()
    old_settings = termios.tcgetattr(file_desc)
    try:
        tty.setraw(sys.stdin.fileno())
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(file_desc, termios.TCSADRAIN, old_settings)
    return char


def get_values(state):
    """Takes a dictionary game state as inputs,
    wwwextracts and returns the values of that dict in a tuple"""
    keys = ['player_ammo', 'player_block', 'player_prev',
            'comp_ammo', 'comp_block', 'comp_prev']
    return tuple([state[key] for key in keys])


def get_move(state):
    """Takes a game state as input,
    returns a move based on locked bool values
    and states weights"""
    entry = game_states[get_values(state)]
    winners = []

    for move in entry:
        move_result = entry[move]
        if move_result == 'Y':
            return move
        elif move_result == 'N':
            continue
        winners += [move]*move_result
    return choice(winners)


def run_match(player_move, comp_move, state):
    """Takes 2 moves and a game state as input,
    updates the curr_state variable,
    returns the game_states entry for the modified state"""
    player_vul = False
    comp_vul = False
    state['player_prev'] = player_move
    state['comp_prev'] = comp_move

    #Update game variables
    if player_move == 'd':
        state['player_ammo'] += 1
        player_vul = True
    if comp_move == 'd':
        state['comp_ammo'] += 1
        comp_vul = True
    if player_move == 'a':
        if comp_vul:
            return 'N'
        state['player_ammo'] -= 1
    if comp_move == 'a':
        if player_vul:
            return 'Y'
        state['comp_ammo'] -= 1

    return game_states[get_values(state)]


def update_game_states(player_move, values):
    """Update game_states with the new data from the players move"""
    if player_move == 'a':
        if game_states[values]['s'] not in ['N', 'Y']:
            game_states[values]['s'] += 1
        elif game_states[values]['a'] not in ['N', 'Y']:
            game_states[values]['a'] += 1

    elif player_move == 's':
        if game_states[values]['d'] not in ['N', 'Y']:
            game_states[values]['d'] += 1
        elif game_states[values]['s'] not in ['N', 'Y']:
            game_states[values]['s'] += 1

    elif player_move == 'd':
        if game_states[values]['a'] not in ['N', 'Y']:
            game_states[values]['a'] += 1
        elif game_states[values]['d'] not in ['N', 'Y']:
            game_states[values]['d'] += 1


def get_player_move(curr_state):
    """Loops until the play enters a valid move"""
    while True:
        print(":")
        player_move = getch()# raw_input(":") #getwch()
        #Confirm player move is valid
        if player_move in ['a', 's', 'd']:
            if player_move == 'a' and not curr_state['player_ammo']:
                print("You can\'t fire")
                continue

            elif player_move == 's' and not curr_state['player_block']:
                print("You can\'t block")
                continue

            elif player_move == 'd' and curr_state['player_ammo'] == 6:
                print("You can\'t reload")
                continue
            break
        else:
            if player_move == 'q':
                print(CLEAR + goodbye_art)
                _exit(0)

            print(CLEAR+"Invalid input\n")
    return player_move


def main(game_round=0):
    """Main function: One run of the function is one game_round of the game"""
    print(CLEAR*2)
    curr_state = {'player_ammo':1, 'player_block':True, 'player_prev':'d',
                  'comp_ammo':1, 'comp_block':True, 'comp_prev':'d'}
    player_blocks = 0
    comp_blocks = 0
    asciis = {'a':gun_art,
              's': shield_art,
              'd':reload_art,
              'Y':loss_art,
              'N':win_art}
    #Main loop
    while True:
        game_round += 1
        print('Round '+str(game_round)+':\n'+' Your Bullets| ' + \
              '*'*curr_state['player_ammo'] + '\n My Bullets  | ' + \
              '*'*curr_state['comp_ammo']+'\n')
        values = get_values(curr_state)
        #First move isn't pulled from game states
        if game_round == 1:
            print("A=FIRE - S=BLOCK - D=RELOAD")
            comp_move = choice(['a', 's', 'd'])
        else:
            #If guaranteed a win, the AI locks itself into firing mode
            if curr_state['comp_ammo'] > (curr_state['player_ammo'] + \
                (3 - player_blocks)):
                comp_move = 'a'
            else:
                comp_move = get_move(curr_state)

        #Player selects move
        player_move = get_player_move(curr_state)

        #Update block variables
        if player_move == 's':
            player_blocks += 1
            if player_blocks == 3:
                curr_state['player_block'] = False
        else:
            player_blocks = 0
            curr_state['player_block'] = True

        if comp_move == 's':
            comp_blocks += 1
            if comp_blocks == 3:
                curr_state['comp_block'] = False
        else:
            comp_blocks = 0
            curr_state['comp_block'] = True



        #print(match
        print(CLEAR + asciis[player_move] +'\n'*2 + \
                  asciis[comp_move] + '\n')

        result = run_match(player_move, comp_move, curr_state)

        #Update game_states with the new data from the players move
        update_game_states(player_move, values)


        if result in ['Y', 'N']:
            with open("states.py", "w") as states:
                states.truncate()
                states.write('game_states='+str(game_states))
                states.close()
            return asciis[result]


if __name__ == '__main__':
    print(main())
    while True:
        print("Press q to exit or any other key to play again ")
        print(sum([val['a'] for val in game_states.values() if type(val['a']) == type(1)]))
        print(sum([val['s'] for val in game_states.values() if type(val['s']) == type(1)]))
        print(sum([val['d'] for val in game_states.values() if type(val['d']) == type(1)]))
        MENU_CHOICE = getch()
        if MENU_CHOICE != 'q':
            print(main())
        else:
            print(CLEAR + goodbye_art)
            _exit(0)
