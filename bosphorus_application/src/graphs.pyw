# coding=utf-8
# Properties:
# - #############Acyclic
# - Connected
# - Directed
# - Finite (by 'reductio ad absurdum')
# - Vertex-transitive
# - Weighted
import graphviz
import os
import time

class CyclicGraphException(Exception):
    pass
class DisconnectedGraphException(Exception):
    pass

class Hyperedge:
    def __init__(self, sources: list, targets: list, weight: int, label: str):
        self.sources: list = sources
        self.targets: list = targets  # Directed
        self.weight: int = weight     # Weighted
        self.label: str = label       # Vertex-transitive
    def __iter__(self):
        return self.targets.__iter__()
    def __getitem__(self, key):
        return self.targets.__getitem__(key)
class Node:
    def __init__(self, label):
        self.label = label
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
        # Therefore: (by search) new node points to itself => Cyclic Graph => raise exception
        # edges = dict(new_node.edges)
        # while(len(edges) > 0):
        #    edges = dict(filter(lambda edge: str(edge.direction) in self.nodes, edges))
        #    if str(new_node.id) in edges:
        #        return False
        #        #raise CyclicGraphException('Node ' + str(new_node.id) + ' has formed a cycle')
        #    edges = dict(reduce(lambda acc, edge: {**acc, **self.nodes[edge.direction].edges}, edges))

        for hyperedge in hyperedges:
            new_nodes = {str(x): Node(x) for x in hyperedge if x not in self}
            self.nodes = {**self.nodes, **new_nodes}

            for source in hyperedge.sources:
                # Add hyperedge into source
                self[str(source)][hyperedge.label] = hyperedge

        return self

    def save_into_disk_and_get_file_name(self, directory: str):
        dot = graphviz.Graph(
            filename=str(time.strftime('%Y_%m_%d_%H_%M_%S')),
            directory=directory,
            format='png'
        )
        for node_label in self:
            dot.node(
                name=node_label
            )
        for source_label in self:
            for edge_label in self[source_label]:
                for target_label in self[source_label][edge_label]:
                    dot.edge(
                        tail_name=str(source_label),
                        head_name=str(target_label),
                        label=edge_label
                    )
        dot.render()

        return os.path.abspath(dot.directory + '/' + dot.filename + '.' + dot.format)

# def test():
#     l0 = (-1, True, True)  # (LOW
#     l1 = (0, True, True)   # (LOW
#     l2 = (0, False, True)  # [0
#     l3 = (0, True, False)  # (0
#     l4 = (1, True, True)   # (LOW
#     l5 = (1, False, True)  # [1
#     l6 = (1, True, False)  # (1
#
#     r0 = (-1, True, True) # HIGH)
#     r1 = (1, True, True)  # HIGH)
#     r2 = (1, False, True) # 1]
#     r3 = (1, True, False) # 1)
#     r4 = (0, True, True)  # HIGH)
#     r5 = (0, False, True) # 0]
#     r6 = (0, True, False) # 0)
#     r7 = (5, False, True) # 5]
#
#     i0 = Interval(l1, r1) # (LOW..HIGH)
#     i1 = Interval(l1, r2) # (LOW..1]
#     i2 = Interval(l1, r3) # (LOW..1)
#     i3 = Interval(l2, r1) # [0..HIGH)
#     i4 = Interval(l2, r2) # [0..1]
#     i5 = Interval(l2, r3) # [0..1)
#     i6 = Interval(l3, r1) # (0..HIGH)
#     i7 = Interval(l3, r2) # (0..1]
#     i8 = Interval(l3, r3) # (0..1)
#     i9 = Interval(l5, r5) # [1..0] -> ()
#     i10 = Interval(l1, r6) # (LOW..0)
#     i11 = Interval(l6, r1) # (1..HIGH)
#     i12 = Interval(l2, r7) # [0..5]
#
#     e0 = IntervalExpression.empty() # ()
#     e1 = IntervalExpression.domain() # (LOW..HIGH)
#
#     edge01 = Edge(
#         direction=str(i1),
#         weight=10,
#         label='send probe')
#     edge02 = Edge(
#         direction=str(i2),
#         weight=10,
#         label='send probe 2')
#     edge12 = Edge(
#         direction=str(i2),
#         weight=10,
#         label='send probe 3')
#     edge13 = Edge(
#         direction=str(i3),
#         weight=20,
#         label='send probe 4')
#
#     node0 = Node(str(i0))
#     node1 = Node(str(i1))
#     node2 = Node(str(i2))
#     node3 = Node(str(i3))
#
#     node0 += edge01
#     node0 += edge02
#     node1 += edge12
#     node1 += edge13
#
#     graph = Graph()
#     graph += node0
#     graph += node1
#     graph += node2
#     graph += node3
#
#     graph.save_into_disk_and_get_file_name()
#
#     while(True):
#         time.sleep(1000)
