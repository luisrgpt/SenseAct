# coding=utf-8
"""Main

"""
import automata
import interface
import generators
import threading
from intervals import LeftEndpoint, RightEndpoint, Interval, IntervalExpression


ship = generators.ship(
    ship_location=[],
    submarine_location=IntervalExpression(
        intervals=[Interval(
            left=LeftEndpoint(0, False, True),
            right=RightEndpoint(100, False, True)
        )]
    ),
    computation_rate=100
)


def init_output():
    """
    :rtype: object

    """
    print("init")
    global ui
    ui.start()
    return 'wait_input'


def ack_init_output():
    """
    :rtype: object

    """
    print("ack init")


def start_output():
    """
    :rtype: object

    """
    print("start")
    global ui
    ui += 'reset', 'next', 'play', 'reset'


def start_play_output():
    """
    :rtype: object

    """
    print("start play")
    global ui, ship
    del ship
    ship = generators.generate_ship([0])
    ui += 'reset'
    return 'start_play_input'


def first_play_output():
    """
    :rtype: object

    """
    print("start play")
    global ui
    ui += 'pause', 'stop', 'repeat-all'
    return 'first_play_input'


def start_next_output():
    """
    :rtype: object

    """
    print("start next")
    global ui, ship
    del ship
    ship = generators.generate_ship([0])
    ui += 'reset', next(ship)
    return 'wait_input'


def ack_play_output():
    """
    :rtype: object

    """
    print("ack play")


def ack_next_output():
    """
    :rtype: object

    """
    print("ack next")


def play_output():
    """
    :rtype: object

    """
    print("play")
    global ui
    ui += next(ship)
    return 'wait_input'


def next_output():
    """
    :rtype: object

    """
    print("next")
    global ui
    ui += next(ship)
    return 'wait_input'


def win_play_output():
    """
    :rtype: object

    """
    print("win play")
    global ui
    ui += 'stop', 'repeat-all'


def win_next_output():
    """
    :rtype: object

    """
    print("win next")
    global ui
    ui += 'stop', 'repeat-all'


def lose_play_output():
    """
    :rtype: object

    """
    print("lose play")
    global ui
    ui += 'stop', 'repeat-all'


def lose_next_output():
    """
    :rtype: object

    """
    print("lose next")
    global ui
    ui += 'stop', 'repeat-all'


def pause_output():
    """
    :rtype: object

    """
    print("pause")
    global ui
    ui += 'previous', 'next', 'play', 'stop', 'repeat-all'


# noinspection PyProtectedMember
def quit_output():
    """
    :rtype: object

    """
    global exit_event
    exit_event.set()

app = automata.Automaton(
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
            'start_next_state': 'ack_next_state',
            'next_state': 'ack_next_state',
            'play_state': 'ack_play_state',
            'init_state': 'ack_init_state',
        },
        'ack_input': {
            'ack_next_state': 'pause_state',
            'ack_play_state': 'play_state',
            'ack_init_state': 'start_state'
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
        'ack_init_state': ack_init_output,
        'play_state': play_output,
        'next_state': next_output,
        'win_play_state': win_play_output,
        'win_next_state': win_next_output,
        'lose_play_state': lose_play_output,
        'lose_next_state': lose_next_output,
        'pause_state': pause_output
    }
)
ui = interface.Handler(app)


# graphs.test()
# intervals.test()
generators.test()
# genetic.test()
# dynamic.test()
app += 'init_input'


exit_event = threading.Event()
exit_event.wait()
