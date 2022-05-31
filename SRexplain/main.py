from manim import *
import networkx as nx
import rich
from sympy import sympify

operator_list = {}



def populate_graph(graph, equation, mother, labels, counter):
    if len(equation.args) == 0:
        counter+=1
        labels[str(equation)+str(counter)] = str(equation)
        graph.add_node(str(equation)+str(len(labels)))
        graph.add_edge(str(equation)+str(len(labels)), mother)
        return graph, labels, counter
    elif len(equation.args) == 1:
        counter+=1
        type_name = type(equation).__name__+str(counter) 
        labels[type_name] = type(equation).__name__
        graph.add_node(type_name)
        graph.add_edge(type_name, mother)
        graph, labels, counter = populate_graph(graph, equation.args[0], type_name, labels, counter)
        return graph, labels, counter
    elif len(equation.args) == 2:
        counter+=1
        type_name = type(equation).__name__+str(counter) 
        labels[type_name] = type(equation).__name__
        graph.add_node(type_name)
        graph.add_edge(type_name, mother)
        graph, labels, counter = populate_graph(graph, equation.args[0], type_name, labels, counter)
        graph, labels, counter = populate_graph(graph, equation.args[1], type_name, labels, counter)
        return graph, labels, counter
    else:
        raise Exception("Too many arguments")

class SRMain(Scene):
    def construct(self):
        G = nx.Graph()
        equation = sympify('4*x+sin(x)')
        G.add_node('ROOT')
        labels = {}
        print(equation.args)
        G, labels, counter = populate_graph(G, equation, 'ROOT', labels, 0)
        root = type(equation).__name__+'1'
        node_list = list(G.nodes)
        edge_list = list(G.edges)
        node_list.remove('ROOT')
        edge_list.remove(('ROOT', root))
        print(node_list, edge_list, labels)
        self.play(Write(Graph(node_list, edge_list, layout="tree", root_vertex=root, labels=labels)),run_time=2)
        self.wait(1)