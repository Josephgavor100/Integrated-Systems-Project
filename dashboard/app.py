import streamlit as st
import pandas as pd
import networkx as nx
from pathlib import Path


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="National Electricity Grid Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "processed" / "processed_data.csv"


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    return pd.read_csv(DATA_FILE)


df = load_data()


# ============================================================
# BUILD NETWORK
# ============================================================

@st.cache_resource
def build_graph(data):

    G = nx.Graph()

    # Add transmission connections
    for _, row in data.iterrows():

        source = row["Source Substation ID"]
        destination = row["Destination Substation ID"]

        G.add_edge(
            source,
            destination
        )

    return G


G = build_graph(df)


# ============================================================
# CALCULATE NETWORK METRICS
# ============================================================

degree = dict(G.degree())

degree_centrality = nx.degree_centrality(G)

betweenness = nx.betweenness_centrality(G)

closeness = nx.closeness_centrality(G)

pagerank = nx.pagerank(G)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚡ GridCare Dashboard")

st.sidebar.markdown(
    """
    **National Electricity Grid Network**

    Interactive analysis of substations,
    transmission lines and network structure.
    """
)

st.sidebar.divider()

st.sidebar.metric(
    "Substations",
    G.number_of_nodes()
)

st.sidebar.metric(
    "Transmission Lines",
    G.number_of_edges()
)


# ============================================================
# HEADER
# ============================================================

st.title("⚡ National Electricity Grid Dashboard")

st.markdown(
    """
    ### Electricity Transmission Network Analysis

    Explore the structure, geographic distribution and
    network importance of substations and transmission lines.
    """
)

st.divider()


# ============================================================
# TABS
# ============================================================

overview_tab, network_tab, map_tab, reliability_tab, search_tab = st.tabs(
    [
        "📊 Overview",
        "🕸️ Network Analysis",
        "🗺️ Geography Map",
        "📈 Reliability / BI",
        "🔎 Substation Search"
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with overview_tab:

    st.header("Grid Overview")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Substations",
            G.number_of_nodes()
        )

    with col2:
        st.metric(
            "Transmission Lines",
            G.number_of_edges()
        )

    with col3:
        st.metric(
            "Connected Components",
            nx.number_connected_components(G)
        )

    with col4:
        st.metric(
            "Network Density",
            f"{nx.density(G):.2%}"
        )

    st.divider()

    st.subheader("Network Summary")

    col1, col2 = st.columns(2)

    with col1:

        highest_degree = max(
            degree,
            key=degree.get
        )

        highest_betweenness = max(
            betweenness,
            key=betweenness.get
        )

        st.info(
            f"**Highest Degree:** Substation {highest_degree} "
            f"({degree[highest_degree]} connections)"
        )

        st.info(
            f"**Highest Betweenness:** Substation "
            f"{highest_betweenness}"
        )

    with col2:

        highest_closeness = max(
            closeness,
            key=closeness.get
        )

        highest_pagerank = max(
            pagerank,
            key=pagerank.get
        )

        st.info(
            f"**Highest Closeness:** Substation "
            f"{highest_closeness}"
        )

        st.info(
            f"**Highest PageRank:** Substation "
            f"{highest_pagerank}"
        )


# ============================================================
# TAB 2 — NETWORK ANALYSIS
# ============================================================

with network_tab:

    st.header("Network Analysis")
        # --------------------------------------------------------
    # NETWORK GRAPH VISUALIZATION
    # --------------------------------------------------------

    network_image = (
        BASE_DIR
        / "grid_analysis"
        / "network_visualization.png"
    )

    if network_image.exists():

        st.subheader("Transmission Network Structure")

        st.image(
            str(network_image),
            caption=(
                "Force-directed network visualization: "
                "node size represents degree and node colour "
                "represents betweenness centrality."
            ),
            use_container_width=True
        )

    else:

        st.warning(
            "Network visualization image has not been generated."
        )

    st.write(
        "Centrality measures identify structurally important "
        "substations within the transmission network."
    )

    metrics_df = pd.DataFrame({

        "Substation": list(G.nodes()),

        "Degree": [
            degree[node]
            for node in G.nodes()
        ],

        "Degree Centrality": [
            degree_centrality[node]
            for node in G.nodes()
        ],

        "Betweenness": [
            betweenness[node]
            for node in G.nodes()
        ],

        "Closeness": [
            closeness[node]
            for node in G.nodes()
        ],

        "PageRank": [
            pagerank[node]
            for node in G.nodes()
        ]
    })

    metrics_df = metrics_df.sort_values(
        "Betweenness",
        ascending=False
    )

    st.dataframe(
        metrics_df,
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Most Structurally Important Substations")

    top5 = metrics_df.head(5)

    st.bar_chart(
        top5.set_index("Substation")[
            "Betweenness"
        ]
    )


# ============================================================
# TAB 3 — GEOGRAPHY MAP
# ============================================================

with map_tab:

    st.header("Geography Map")

    map_file = (
        BASE_DIR
        / "grid_analysis"
        / "substation_map.html"
    )

    if map_file.exists():

        st.components.v1.html(
            map_file.read_text(
                encoding="utf-8"
            ),
            height=700,
            scrolling=True
        )

    else:

        st.warning(
            "GIS map has not been generated yet."
        )


# ============================================================
# TAB 4 — RELIABILITY / BI
# ============================================================

with reliability_tab:

    st.header("Reliability / Business Intelligence")

    st.info(
        "Reliability and BI visualizations will be integrated "
        "here from the team's exploratory and reliability analysis."
    )

    st.subheader("Line Status")

    if "Line Status" in df.columns:

        status_counts = (
            df["Line Status"]
            .value_counts()
        )

        st.bar_chart(status_counts)

    st.subheader("Voltage Distribution")

    if "Line Voltage (kV)" in df.columns:

        voltage_counts = (
            df["Line Voltage (kV)"]
            .value_counts()
            .sort_index()
        )

        st.bar_chart(voltage_counts)


# ============================================================
# TAB 5 — SUBSTATION SEARCH
# ============================================================

with search_tab:

    st.header("Substation Search")

    st.write(
        "Search for a substation and view its network metrics."
    )

    substation_ids = sorted(
        [str(node) for node in G.nodes()]
    )

    selected_id = st.selectbox(
        "Select Substation",
        substation_ids
    )

    selected_node = int(selected_id)

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Degree",
            degree[selected_node]
        )

    with col2:
        st.metric(
            "Degree Centrality",
            f"{degree_centrality[selected_node]:.3f}"
        )

    with col3:
        st.metric(
            "Betweenness",
            f"{betweenness[selected_node]:.3f}"
        )

    with col4:
        st.metric(
            "PageRank",
            f"{pagerank[selected_node]:.4f}"
        )

    st.divider()

    # Find information about selected substation
    source_match = df[
        df["Source Substation ID"] == selected_node
    ]

    destination_match = df[
        df["Destination Substation ID"] == selected_node
    ]

    if not source_match.empty:

        row = source_match.iloc[0]

        st.subheader("Substation Information")

        info_col1, info_col2 = st.columns(2)

        with info_col1:

            st.write(
                f"**Name:** {row['Source Substation']}"
            )

            st.write(
                f"**Region:** {row['Source Region']}"
            )

            st.write(
                f"**Voltage:** {row['Source Voltage (kV)']} kV"
            )

        with info_col2:

            st.write(
                f"**Capacity:** {row['Source Capacity (MVA)']} MVA"
            )

            st.write(
                f"**Status:** {row['Source Status']}"
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Integrated Systems Project | Electricity Grid Analysis"
)
