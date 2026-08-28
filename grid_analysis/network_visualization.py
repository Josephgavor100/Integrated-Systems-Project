import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt


# ============================================================
# 1. LOAD DATA
# ============================================================

SUBSTATIONS_FILE = "../data/raw/substations.csv"
LINES_FILE = "../data/processed/processed_data.csv"

substations = pd.read_csv(SUBSTATIONS_FILE)
lines = pd.read_csv(LINES_FILE)


# ============================================================
# 2. BUILD NETWORK
# ============================================================

G = nx.Graph()

# Add substations as nodes
G.add_nodes_from(substations["Substation ID"])

# Add transmission lines as edges
for _, row in lines.iterrows():
    G.add_edge(
        row["Source Substation ID"],
        row["Destination Substation ID"]
    )


# ============================================================
# 3. ADD NODE ATTRIBUTES
# ============================================================

for _, row in substations.iterrows():

    station_id = row["Substation ID"]

    G.nodes[station_id]["Name"] = row["Name"]
    G.nodes[station_id]["Region"] = row["Region"]
    G.nodes[station_id]["Voltage"] = row["Voltage (kV)"]
    G.nodes[station_id]["Capacity"] = row["Capacity (MVA)"]


# ============================================================
# 4. NETWORK METRICS
# ============================================================

degree = dict(G.degree())

betweenness = nx.betweenness_centrality(G)

closeness = nx.closeness_centrality(G)

pagerank = nx.pagerank(G)


# ============================================================
# 5. FORCE-DIRECTED LAYOUT
# ============================================================

positions = nx.spring_layout(
    G,
    seed=42,
    k=0.8,
    iterations=100
)


# ============================================================
# 6. NODE SIZES
# ============================================================

# Larger degree = larger node
node_sizes = [
    300 + (degree[node] * 180)
    for node in G.nodes()
]


# ============================================================
# 7. NODE IMPORTANCE
# ============================================================

# Use betweenness to identify structurally important nodes
node_colors = [
    betweenness[node]
    for node in G.nodes()
]


# ============================================================
# 8. DRAW NETWORK
# ============================================================

plt.figure(figsize=(16, 11))

nodes = nx.draw_networkx_nodes(
    G,
    positions,
    node_size=node_sizes,
    node_color=node_colors,
    cmap="viridis",
    alpha=0.9,
    edgecolors="black",
    linewidths=0.8
)

nx.draw_networkx_edges(
    G,
    positions,
    width=1.5,
    alpha=0.6
)


# ============================================================
# 9. LABEL NODES
# ============================================================

labels = {
    node: str(node)
    for node in G.nodes()
}

nx.draw_networkx_labels(
    G,
    positions,
    labels=labels,
    font_size=8
)


# ============================================================
# 10. HIGHLIGHT IMPORTANT SUBSTATIONS
# ============================================================

highest_betweenness = max(
    betweenness,
    key=betweenness.get
)

highest_pagerank = max(
    pagerank,
    key=pagerank.get
)

highest_closeness = max(
    closeness,
    key=closeness.get
)


# Highlight highest betweenness
nx.draw_networkx_nodes(
    G,
    positions,
    nodelist=[highest_betweenness],
    node_size=900,
    node_color="red",
    edgecolors="black",
    linewidths=2
)


# ============================================================
# 11. TITLE
# ============================================================

plt.title(
    "Electricity Transmission Network\n"
    "Node Size = Degree | Node Colour = Betweenness Centrality",
    fontsize=18
)


plt.axis("off")


# ============================================================
# 12. COLORBAR
# ============================================================

plt.colorbar(
    nodes,
    label="Betweenness Centrality"
)


# ============================================================
# 13. SAVE OUTPUT
# ============================================================

plt.tight_layout()

plt.savefig(
    "network_visualization.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# 14. PRINT KEY RESULTS
# ============================================================

print("\nNETWORK VISUALIZATION CREATED")
print("--------------------------------")

print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

print(
    f"Highest Betweenness: "
    f"Substation {highest_betweenness}"
)

print(
    f"Highest Closeness: "
    f"Substation {highest_closeness}"
)

print(
    f"Highest PageRank: "
    f"Substation {highest_pagerank}"
)

print("\nOutput:")
print("network_visualization.png")