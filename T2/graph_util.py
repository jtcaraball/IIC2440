import json
from itertools import permutations
from random import sample, randint
from sys import argv


MODE_OPTIONS = ['simple', 'costs']
MIN_COST = 1
MAX_COST = 10


def generate_graph(n_nodes: int, n_edges: int) -> tuple[list, list]:
    if n_edges > n_nodes * (n_nodes - 1):
        raise Exception('Maximum edges surpassed.')

    nodes = [i for i in range(1, n_nodes + 1)]
    clique = list(permutations(nodes, 2))
    edges = sample(clique, n_edges)
    return nodes, edges


def write_graph(path: str, nodes: list[int], edges: list) -> None:
    with open(path, 'w') as file:
        json.dump(
            {'nodes': nodes, 'edges': edges},
            file,
            indent=4
        )


def create_graph(path: str, n_nodes: int, n_edges: int) -> None:
    nodes, edges = generate_graph(n_nodes, n_edges)
    write_graph(path, nodes, edges)


def create_graph_with_costs(
    path: str,
    n_nodes: int,
    n_edges: int
) -> None:
    nodes, edges = generate_graph(n_nodes, n_edges)
    edges_with_cost = [
        (start, end, randint(MIN_COST, MAX_COST))
        for start, end in edges
    ]
    write_graph(path, nodes, edges_with_cost)


def valid_input(mode: str, n_nodes: str, n_edges: str) -> bool:
    valid_mode = mode in MODE_OPTIONS
    valid_digits = n_nodes.isdigit() and n_edges.isdigit()
    valid_range = int(n_nodes) > 0 and int(n_edges) > 0
    return valid_mode and valid_digits and valid_range


if __name__ == "__main__":
    _, mode, n_nodes, n_edges = argv
    if not valid_input(mode, n_nodes, n_edges):
        print(
            'Use -> graph_util.py mode:[simple, costs]',
            'n_nodes:[int > 0] n_edges:[int > 0]'
        )
        exit(1)
    if mode == 'simple':
        create_graph('graph.json', int(n_nodes), int(n_edges))
        exit(0)
    create_graph_with_costs('graph_costs.json', int(n_nodes), int(n_edges))
    exit(0)
