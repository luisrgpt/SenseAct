# Properties:
# - #############Acyclic
# - Connected
# - Directed
# - Finite (by 'reductio ad absurdum')
# - Vertex-transitive
# - Weighted
import os

#import graphviz

class CyclicGraphException(Exception):
  pass

class DisconnectedGraphException(Exception):
  pass

class Hyperedge:

  def __init__(self, sources: list, targets: list, weight: int, label: str):
    self.sources: list = sources
    self.targets: list = targets  # Directed
    self.weight: int = weight  # Weighted
    self.label: str = label  # Vertex-transitive

  def __iter__(self):
    return self.targets.__iter__()

  def __getitem__(self, key):
    return self.targets.__getitem__(key)

class Node:

  def __init__(self, label):
    self.label = str(label)
    self.edges: dict = {}

  def __iter__(self):
    return self.edges.__iter__()

  def __getitem__(self, key):
    return self.edges.__getitem__(key)

  def __setitem__(self, key, value):
    return self.edges.__setitem__(key, value)

class Graph:

  def __init__(self, node: Node):
    self.nodes: dict = {str(node.label): node}

  def __iter__(self):
    return self.nodes.__iter__()

  def __getitem__(self, key):
    return self.nodes.__getitem__(key)

  def __contains__(self, node: Node):
    return str(node) in self.nodes

  def __iadd__(self, hyperedges):
    # Connected Graph => ANY node in graph points to new node
    # Therefore: EVERY node in graph does NOT point to new node => Disconnected Graph => raise exception
    # if not len(self.nodes) == 0 and not any(str(new_node.id) in node.edges for node in self.nodes[0]s()):
    #    raise DisconnectedGraphException('Node ' + str(new_node.id) + ' is disconnected from graph')

    # Acyclic Graph => new node does not point to itself
    # Therefore: (by senseact_dynamic_programming) new node points to itself => Cyclic Graph => raise exception
    # edges = dict(new_node.edges)
    # while(len(edges) > 0):
    #    edges = dict(filter(lambda edge: str(edge.direction) in self.nodes, edges))
    #    if str(new_node.id) in edges:
    #        return False
    #        #raise CyclicGraphException('Node ' + str(new_node.id) + ' has formed a cycle')
    #    edges = dict(reduce(lambda acc, edge: {**acc, **self.nodes[edge.direction].edges}, edges))

    for hyperedge in hyperedges:
      for target in hyperedge:
        if target not in self:
          self.nodes[str(target)] = Node(target)

      for source in hyperedge.sources:
        # Add hyperedge into source
        self[str(source)][hyperedge.label] = hyperedge

    return self

  # def export_png(self, directory: str, filename: str):
  #   dot = graphviz.Graph(
  #     filename=filename,
  #     directory=directory,
  #     format='png'
  #   )
  #   for node_label in self:
  #     dot.node(
  #       name=node_label
  #     )
  #
  #   legends = []
  #   for source_label in self:
  #     for edge_label in self[source_label]:
  #       for target_label in self[source_label][edge_label]:
  #         if edge_label in legends:
  #           label = '[' + str(legends.index(edge_label) + 1) + ']'
  #         else:
  #           legends += [edge_label]
  #           label = '[' + str(len(legends)) + ']'
  #         dot.edge(
  #           tail_name=str(source_label),
  #           head_name=str(target_label),
  #           label=label
  #         )
  #
  #   with dot.subgraph(name='Legends', graph_attr={'rankdir': 'LR'},
  #                     node_attr={'shape': 'plaintext'}) as sub_dot:
  #     for index, label in enumerate(legends):
  #       sub_dot.node(
  #         name='[' + str(index + 1) + ']' + ": " + label
  #       )
  #
  #   dot.render(
  #     cleanup=True
  #   )
  #
  #   return os.path.abspath(
  #     dot.directory + '/' + dot.filename + '.' + dot.format)
