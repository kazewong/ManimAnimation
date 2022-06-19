from manim import *
import networkx as nx


def populate_graph(graph, equation, mother, labels, counter):
    if len(equation.args) == 0:
        counter+=1
        if type(equation).__name__ == 'Symbol':
            labels[str(equation)+str(counter)] = str(equation)[:3]
        else:
            labels[str(equation)+str(counter)] = str(equation)[:3]
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
        graph, labels, counter = populate_graph(graph, equation.args[1], type_name, labels, counter)
        graph, labels, counter = populate_graph(graph, equation.args[0], type_name, labels, counter)
        return graph, labels, counter
    else:
        counter+=1
        type_name = type(equation).__name__+str(counter) 
        labels[type_name] = type(equation).__name__
        graph.add_node(type_name)
        graph.add_edge(type_name, mother)
        for i in range(len(equation.args)):
            graph, labels, counter = populate_graph(graph, equation.args[i], type_name, labels, counter)
        return graph, labels, counter

def get_graph(equation):
    G = nx.Graph()
    G.add_node('ROOT')
    labels = {}
    G, labels, counter = populate_graph(G, equation, 'ROOT', labels, 0)
    root = type(equation).__name__+'1'
    node_list = list(G.nodes)
    edge_list = list(G.edges)
    node_list.remove('ROOT')
    edge_list.remove(('ROOT', root))
    graph = Graph(node_list, edge_list, layout="tree", root_vertex=root, labels=labels, layout_config={'vertex_spacing':(1.5,1.5)},vertex_config={'radius':0.5})
    return graph
    