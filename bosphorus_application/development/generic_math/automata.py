class AutomatonException(Exception):
  pass

class Automaton:

  def __init__(self, state_transitions: dict, state_outputs: dict):
    self.state_transitions = state_transitions
    self.state_outputs = state_outputs
    self.current_state = None

  def __iadd__(self, input_name: str):
    if input_name not in self.state_transitions:
      return
      # raise AutomatonException(
      #     'Input ' + input_name + ' does not apply in state ' + self.current_state
      # )

    while input_name is not None:
      next_state = self.state_transitions[input_name]
      self.current_state = (
        next_state if isinstance(next_state, str)
        else
        next_state[self.current_state]
      )
      input_name = self.state_outputs[self.current_state]()

    return self
