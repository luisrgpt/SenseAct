from functools import reduce
# Properties:
# - #############Acyclic
# - Connected
# - Directed
# - Finite (by "reductio ad absurdum")
# - Vertex-transitive
# - Weighted

class CyclicGraphException(Exception):
    pass

class DisconnectedGraphException(Exception):
    pass

class Edge:
    def __init__(self, directions, weight, condition):
        self.directions = directions # Directed
        self.weight = weight         # Weighted
        self.condition = condition   # Vertex-transitive

class Node:
    def __init__(self, id, edges):
        self.id = id
        self.edges: dict = {}

class Graph:
    def __init__(self):
        self.nodes: dict = {}

    def try_add(self, new_node):
        self.nodes[str(new_node.id)] = new_node
        
        # Connected Graph => ANY node in graph points to new node
        # Therefore: EVERY node in graph does NOT point to new node => Disconnected Graph => raise exception
        if all(not str(new_node.id) in node.edges for node in self.nodes):
            raise DisconnectedGraphException("Node " + str(new_node.id) + " is disconnected from graph")
        
        # Acyclic Graph => new node does not point to itself
        # Therefore: (by search) new node points to itself => Cyclic Graph => raise exception
        #edges = dict(new_node.edges)
        #while(len(edges) > 0):
        #    edges = dict(filter(lambda edge: str(edge.direction) in self.nodes, edges))
        #    if str(new_node.id) in edges:
        #        return False
        #        #raise CyclicGraphException("Node " + str(new_node.id) + " has formed a cycle")
        #    edges = dict(reduce(lambda acc, edge: {**acc, **self.nodes[edge.direction].edges}, edges))

        return True