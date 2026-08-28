"""
grid_analysis/graph_analytics.py
Member 2 (Adwoa) Module: Network Topology & N-1 Contingency Analysis
"""

import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from typing import Dict, Tuple, Any, Optional


class GridNetworkAnalyzer:
    def __init__(self, data_path: str = "data/processed/processed_data.csv", substations_path: Optional[str] = None, lines_path: Optional[str] = None):
        # Support both a single processed file or separate paths
        self.data_path = substations_path or data_path
        self.lines_path = lines_path
        self.graph = nx.Graph()
        self.df = None

    def load_data_and_build_graph(self) -> nx.Graph:
        """Loads clean substation and line datasets (or combined processed CSV) and constructs the NetworkX graph."""
        self.graph.clear()
        
        # Scenario A: Separate files mode
        if self.lines_path:
            substations_df = pd.read_csv(self.data_path)
            lines_df = pd.read_csv(self.lines_path)

            for _, row in substations_df.iterrows():
                self.graph.add_node(
                    str(row['substation_id']),
                    name=row.get('name', f"Substation {row['substation_id']}"),
                    region=row.get('region', 'Unknown'),
                    capacity=row.get('capacity_mw', 0)
                )

            for _, row in lines_df.iterrows():
                self.graph.add_edge(
                    str(row['source_id']),
                    str(row['target_id']),
                    line_id=row.get('line_id'),
                    status=row.get('status', 'Active'),
                    capacity=row.get('capacity_mw', 100)
                )
        
        # Scenario B: Single combined processed_data.csv mode
        else:
            self.df = pd.read_csv(self.data_path)

            for _, row in self.df.iterrows():
                # Add Source Substation Node
                src_id = str(row['Source Substation ID'])
                if not self.graph.has_node(src_id):
                    self.graph.add_node(
                        src_id,
                        name=row.get('Source Substation', f"Substation {src_id}"),
                        region=row.get('Source Region', 'Unknown'),
                        voltage=row.get('Source Voltage (kV)', 0)
                    )

                # Add Destination Substation Node
                dst_id = str(row['Destination Substation ID'])
                if not self.graph.has_node(dst_id):
                    self.graph.add_node(
                        dst_id,
                        name=row.get('Destination Substation', f"Substation {dst_id}"),
                        region=row.get('Destination Region', 'Unknown'),
                        voltage=row.get('Destination Voltage (kV)', 0)
                    )

                # Add Edge (Power Line)
                self.graph.add_edge(
                    src_id,
                    dst_id,
                    line_id=str(row.get('Line ID')),
                    status=row.get('Line Status', 'Active'),
                    capacity=row.get('Line Capacity (MVA)', 100)
                )

        return self.graph

    def calculate_centrality_metrics(self) -> pd.DataFrame:
        """Calculates degree and betweenness centrality for all nodes."""
        if self.graph.number_of_nodes() == 0:
            self.load_data_and_build_graph()

        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph)

        metrics = []
        for node in self.graph.nodes():
            metrics.append({
                'substation_id': node,
                'name': self.graph.nodes[node].get('name'),
                'region': self.graph.nodes[node].get('region'),
                'degree': self.graph.degree(node),
                'degree_centrality': round(degree_centrality[node], 4),
                'betweenness_centrality': round(betweenness_centrality[node], 4)
            })

        return pd.DataFrame(metrics).sort_values(by='betweenness_centrality', ascending=False)

    def run_n1_contingency(self) -> Dict[str, Any]:
        """
        Simulates single-element failure (N-1) across all edges.
        Identifies critical lines that cause network fragmentation.
        """
        if self.graph.number_of_nodes() == 0:
            self.load_data_and_build_graph()

        initial_components = nx.number_connected_components(self.graph)
        critical_lines = []

        for u, v, data in self.graph.edges(data=True):
            temp_graph = self.graph.copy()
            temp_graph.remove_edge(u, v)

            new_components = nx.number_connected_components(temp_graph)

            if new_components > initial_components:
                critical_lines.append({
                    'line_id': data.get('line_id', f"{u}-{v}"),
                    'source': u,
                    'target': v,
                    'impact_components': new_components
                })

        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'is_connected': nx.is_connected(self.graph),
            'critical_n1_lines': critical_lines
        }

    def render_network_figure(self) -> Figure:
        """Renders a Matplotlib figure of the grid network for UI embedding."""
        if self.graph.number_of_nodes() == 0:
            self.load_data_and_build_graph()

        fig, ax = plt.subplots(figsize=(6, 4.5), facecolor='#ffffff')
        pos = nx.spring_layout(self.graph, seed=42)

        nx.draw_networkx_nodes(self.graph, pos, node_size=300, node_color='#3b82f6', ax=ax)
        nx.draw_networkx_edges(self.graph, pos, edge_color='#9ca3af', width=1.5, ax=ax)
        nx.draw_networkx_labels(self.graph, pos, font_size=8, font_color='black', ax=ax)

        ax.set_title("National Power Grid Topology", fontsize=12, fontweight='bold')
        ax.axis('off')
        fig.tight_layout()
        return fig