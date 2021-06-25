#!/usr/bin/env python3

import argparse
import networkx as nx
import matplotlib.pyplot as plt

from mas_execution.sm_loader import SMLoader

if __name__ == '__main__':
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-sm', '--sm_path', type=str, required=True,
                           help='Path to a state machine definition file')
    argparser.add_argument('-psm', '--parent_sm_path', type=str, default=None,
                           help='Path to a parent state machine definition file')

    args = argparser.parse_args()
    sm_path = args.sm_path
    parent_sm_path = args.parent_sm_path
    sm_data = None
    if parent_sm_path is not None:
        sm_data = SMLoader.load_sm(sm_path, parent_sm_path)
    else:
        sm_data = SMLoader.load_sm(args.sm_path)

    graph = nx.DiGraph()
    for _, state in sm_data.state_params.items():
        for transition, resulting_state in state.transitions.items():
            graph.add_edge(state.name, resulting_state)

    init_state = list(sm_data.state_params.keys())[0]
    sink_nodes = [node for node in graph.nodes
                  if graph.out_degree(node) == 0]

    node_positions = nx.planar_layout(graph)
    nx.draw(graph, node_positions, with_labels=True)
    nx.draw_networkx_nodes(graph, node_positions, nodelist=[init_state], node_color='g')
    nx.draw_networkx_nodes(graph, node_positions, nodelist=sink_nodes, node_color='r')
    plt.show()
