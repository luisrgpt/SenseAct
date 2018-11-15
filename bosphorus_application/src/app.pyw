# coding=utf-8
############################################################










############################################################
from automata import Automaton
from frontend import Handler
from backend import search

from submarine import Parameters
#from forest_fires import Parameters
############################################################










############################################################
def init_output():
    print('init')
    global frontend
    frontend.start()
def start_output():
    print('start')
    global frontend
    frontend += 'reset', 'next', 'play', 'reset'
def start_play_output():
    print('start play')
    global frontend, backend
    del backend
    backend = search(parameters=Parameters)
    frontend += 'reset'
    return 'start_play_input'
def first_play_output():
    print('start play')
    global frontend
    frontend += 'pause', 'stop', 'repeat-all'
    return 'first_play_input'
def start_next_output():
    print('start next')
    global frontend, backend
    del backend
    backend = search(parameters=Parameters)
    frontend += 'reset', next(backend)
def ack_play_output():
    print('ack play')
def ack_next_output():
    print('ack next')
def play_output():
    print('play')
    global frontend
    frontend += next(backend)
    return 'wait_input'
def next_output():
    print('next')
    global frontend
    frontend += next(backend)
    return 'wait_input'
def win_play_output():
    print('win play')
    global frontend
    frontend += 'stop', 'repeat-all'
def win_next_output():
    print('win next')
    global frontend
    frontend += 'stop', 'repeat-all'
def lose_play_output():
    print('lose play')
    global frontend
    frontend += 'stop', 'repeat-all'
def lose_next_output():
    print('lose next')
    global frontend
    frontend += 'stop', 'repeat-all'
def pause_output():
    print('pause')
    global frontend
    frontend += 'previous', 'next', 'play', 'stop', 'repeat-all'
def quit_output():
    #global exit_event
    #exit_event.set()
    pass
############################################################










############################################################
app = Automaton(
    state_transitions={
        'init_input': 'init_state',
        'quit_input': 'quit_state',
        'start_input': {
            'init_state': 'start_state'
        },
        'start_play_input': {
            'start_play_state': 'first_play_state'
        },
        'wait_input': {
            'next_state': 'ack_next_state',
            'play_state': 'ack_play_state',
        },
        'ack_input': {
            'start_next_state': 'pause_state',
            'ack_next_state': 'pause_state',
            'ack_play_state': 'play_state',
            'init_state': 'start_state'
        },
        'next_input': {
            'start_state': 'start_next_state',
            'pause_state': 'next_state'
        },
        'first_play_input': {
            'first_play_state': 'play_state'
        },
        'play_input': {
            'start_state': 'start_play_state',
            'pause_state': 'first_play_state'
        },
        'pause_play_input': {
            'play_state': 'pause_state'
        },
        'stop_input': {
            'play_state': 'start_state',
            'pause_state': 'start_state',
            'win_play_state': 'start_state',
            'win_next_state': 'start_state',
            'lose_play_state': 'start_state',
            'lose_next_state': 'start_state',
            'ack_play_state': 'start_state',
            'first_play_state': 'start_state'
        },
        'repeat_all_input': {
            'play_state': 'start_play_state',
            'pause_state': 'start_next_state',
            'win_play_state': 'start_play_state',
            'win_next_state': 'start_next_state',
            'lose_play_state': 'start_play_state',
            'lose_next_state': 'start_next_state',
            'ack_play_state': 'start_play_state',
            'first_play_state': 'start_play_state'
        },
        'win_input': {
            'play_state': 'win_play_state',
            'next_state': 'win_next_state'
        },
        'lose_input': {
            'play_state': 'lose_play_state',
            'next_state': 'lose_next_state'
        }
    },
    state_outputs={
        'init_state': init_output,
        'quit_state': quit_output,
        'start_state': start_output,
        'start_play_state': start_play_output,
        'start_next_state': start_next_output,
        'first_play_state': first_play_output,
        'ack_play_state': ack_play_output,
        'ack_next_state': ack_next_output,
        'play_state': play_output,
        'next_state': next_output,
        'win_play_state': win_play_output,
        'win_next_state': win_next_output,
        'lose_play_state': lose_play_output,
        'lose_next_state': lose_next_output,
        'pause_state': pause_output
    }
)
backend = search(parameters=Parameters)
frontend = Handler(app)

app += 'init_input'
