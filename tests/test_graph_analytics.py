import sys
import os
from pathlib import Path
import pytest

# Add project root directory to sys.path before importing local modules
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from grid_analysis.graph_analytics import GridNetworkAnalyzer


@pytest.fixture
def analyzer_instance():
    data_file = PROJECT_ROOT / "data" / "processed" / "processed_data.csv"
    analyzer = GridNetworkAnalyzer(data_path=str(data_file))
    analyzer.load_data_and_build_graph()
    return analyzer


def test_graph_initialization(analyzer_instance):
    """Verify nodes and edges are populated in the network graph."""
    assert analyzer_instance.graph is not None
    assert analyzer_instance.graph.number_of_nodes() > 0
    assert analyzer_instance.graph.number_of_edges() > 0


def test_centrality_metrics(analyzer_instance):
    """Ensure degree and betweenness metrics return non-empty DataFrames."""
    df_metrics = analyzer_instance.calculate_centrality_metrics()
    assert not df_metrics.empty
    assert "degree" in df_metrics.columns
    assert "betweenness_centrality" in df_metrics.columns


def test_n1_contingency_analysis(analyzer_instance):
    """Ensure N-1 contingency run correctly detects critical lines."""
    contingency_res = analyzer_instance.run_n1_contingency()
    assert isinstance(contingency_res, dict)
    assert "critical_n1_lines" in contingency_res
    assert isinstance(contingency_res["critical_n1_lines"], list)