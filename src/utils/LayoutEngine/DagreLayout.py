import networkx as nx


class DagreLayout:
    def __init__(self, automaton_builder, node_spacing=50, rank_spacing=100):
        self._automaton_builder = automaton_builder
        self._node_spacing = node_spacing
        self._rank_spacing = rank_spacing
        self._positions = self._calculate_positions()

    def _calculate_positions(self):
        graph = self._build_graph()
        ranks = self._assign_ranks(graph)
        ordered_ranks = self._order_nodes(graph, ranks)
        positions = self._position_nodes(ordered_ranks)
        return positions

    def _build_graph(self):
        graph = nx.DiGraph()
        for state in self._automaton_builder.states:
            graph.add_node(state.id)
        for state in self._automaton_builder.states:
            for transition in self._automaton_builder.get_transitions_from_state(state.id):
                graph.add_edge(state.id, transition.state_to.id)
        return graph

    def _assign_ranks(self, graph):
        ranks = {}
        for node in nx.topological_sort(graph):
            if graph.in_degree(node) == 0:
                ranks[node] = 0
            else:
                ranks[node] = max(ranks[pred] + 1 for pred in graph.predecessors(node))
        return ranks

    def _order_nodes(self, graph, ranks):
        ordered_ranks = {}
        for node, rank in ranks.items():
            if rank not in ordered_ranks:
                ordered_ranks[rank] = []
            ordered_ranks[rank].append(node)
        for rank in ordered_ranks:
            ordered_ranks[rank].sort(key=lambda node: graph.out_degree(node), reverse=True)
        return ordered_ranks

    def _position_nodes(self, ordered_ranks):
        positions = {}
        for rank, nodes in ordered_ranks.items():
            y = rank * self._rank_spacing
            x_start = (len(nodes) - 1) * self._node_spacing / -2
            for i, node in enumerate(nodes):
                x = x_start + i * self._node_spacing
                positions[node] = (x, y)
        return positions

    @property
    def positions(self):
        return self._positions
