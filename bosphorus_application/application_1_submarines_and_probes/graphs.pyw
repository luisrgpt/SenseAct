# coding=utf-8
"""Graphs

"""

import graphviz
# from intervals import LeftEndpoint, RightEndpoint, Interval, IntervalExpression
import os
import time

# Properties:
# - #############Acyclic
# - Connected
# - Directed
# - Finite (by 'reductio ad absurdum')
# - Vertex-transitive
# - Weighted


class CyclicGraphException(Exception):
    """Cyclic graph exception

    """
    pass


class DisconnectedGraphException(Exception):
    """Disconnected graph exception

    """
    pass

# class Edge:
#    def __init__(self, target: str, weight: int, label: str):
#        self.target: str = target # Directed
#        self.weight: int = weight # Weighted
#        self.label: str = label   # Vertex-transitive


class Hyperedge:
    """Hyperedge

    """
    def __init__(self, sources: list, targets: list, weight: int, label: str):
        self.sources: list = sources
        self.targets: list = targets  # Directed
        self.weight: int = weight     # Weighted
        self.label: str = label       # Vertex-transitive


class Node:
    """Node

    """
    def __init__(self, label):
        self.label = label
        self.edges: dict = {}


class Graph:
    """Graph

    """
    def __init__(self, node: Node):
        self.nodes: dict = {str(node.label): node}

    def __iadd__(self, hyperedge: Hyperedge):
        # Connected Graph => ANY node in graph points to new node
        # Therefore: EVERY node in graph does NOT point to new node => Disconnected Graph => raise exception
        # if not len(self.nodes) == 0 and not any(str(new_node.id) in node.edges for node in self.nodes.values()):
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

        for target in hyperedge.targets:
            # Add target into graph
            self.nodes[str(target)] = Node(target)

        for source in hyperedge.sources:
            # Add hyperedge into source
            self.nodes[str(source)].edges[hyperedge.label] = hyperedge

        return self

    def save_into_disk_and_get_file_name(self, directory: str):
        """

        :param directory:
        :return:
        """
        dot = graphviz.Graph(
            filename=str(time.strftime('%Y_%m_%d_%H_%M_%S')),
            directory=directory,
            format='png'
        )
        for node_id in self.nodes:
            dot.node(
                name=node_id
            )
        for source in self.nodes.values():
            for edge in source.edges.values():
                for target in edge.targets:
                    dot.edge(
                        tail_name=str(source.id),
                        head_name=str(target),
                        label=edge.label
                    )
        dot.render()

        return os.path.abspath(dot.directory + '/' + dot.filename + '.' + dot.format)


# def test():
#     l0 = LeftEndpoint(-1, True, True)  # (LOW
#     l1 = LeftEndpoint(0, True, True)   # (LOW
#     l2 = LeftEndpoint(0, False, True)  # [0
#     l3 = LeftEndpoint(0, True, False)  # (0
#     l4 = LeftEndpoint(1, True, True)   # (LOW
#     l5 = LeftEndpoint(1, False, True)  # [1
#     l6 = LeftEndpoint(1, True, False)  # (1
#
#     r0 = RightEndpoint(-1, True, True) # HIGH)
#     r1 = RightEndpoint(1, True, True)  # HIGH)
#     r2 = RightEndpoint(1, False, True) # 1]
#     r3 = RightEndpoint(1, True, False) # 1)
#     r4 = RightEndpoint(0, True, True)  # HIGH)
#     r5 = RightEndpoint(0, False, True) # 0]
#     r6 = RightEndpoint(0, True, False) # 0)
#     r7 = RightEndpoint(5, False, True) # 5]
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
