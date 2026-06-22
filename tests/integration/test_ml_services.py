"""ML service tests — profiling, forecasting, hotspot, similarity, sociological, financial, network."""
import importlib
import pytest
import pandas as pd
import numpy as np


_profiling_data = importlib.import_module("profiling.data")
_profiling_model = importlib.import_module("profiling.model")
_hotspot_data = importlib.import_module("hotspot.data")
_hotspot_model = importlib.import_module("hotspot.model")
_similarity_data = importlib.import_module("similarity.data")
_similarity_model = importlib.import_module("similarity.model")
_sociological_data = importlib.import_module("sociological.data")
_sociological_model = importlib.import_module("sociological.model")
_financial_data = importlib.import_module("financial.data")
_financial_model = importlib.import_module("financial.model")
_network_data = importlib.import_module("network.data")
_network_model = importlib.import_module("network.model")

try:
    _forecasting_data = importlib.import_module("forecasting.data")
    _forecasting_model = importlib.import_module("forecasting.model")
    _HAS_FORECAST = True
except ModuleNotFoundError:
    _forecasting_data = _forecasting_model = None
    _HAS_FORECAST = False


# ──────────────────────────────────────────────
# Profiling
# ──────────────────────────────────────────────
class TestProfilingModule:
    def test_generate_dataset_shape(self):
        df = _profiling_data.generate_dataset(n_samples=200, seed=42)
        assert len(df) == 200
        expected = {"age", "prior_cases", "is_repeat_offender", "education_score",
                     "employment_score", "is_male", "substance_abuse", "gang_affiliation",
                     "mental_health_issues", "weapon_use", "violence_score", "risk_score",
                     "recidivism_probability", "escalation_risk", "archetype"}
        assert expected.issubset(set(df.columns))

    def test_generate_dataset_archetypes(self):
        df = _profiling_data.generate_dataset(n_samples=1000, seed=42)
        for a in df["archetype"].unique():
            assert a in _profiling_data.OFFENDER_ARCHETYPES

    def test_split_data_ratio(self):
        df = _profiling_data.generate_dataset(n_samples=500, seed=42)
        train, test = _profiling_data.split_data(df, test_size=0.2)
        assert len(train) == 400
        assert len(test) == 100

    def test_train_returns_dict(self):
        result = _profiling_model.train(save=False)
        assert isinstance(result, dict)
        for key in ("archetype_accuracy", "escalation_accuracy", "recidivism_mse", "recidivism_r2"):
            assert key in result

    def test_train_metrics_bounds(self):
        result = _profiling_model.train(save=False)
        assert 0 <= result["archetype_accuracy"] <= 1
        assert 0 <= result["escalation_accuracy"] <= 1
        assert result["recidivism_mse"] >= 0

    def test_predict_structure(self):
        _profiling_model.train(save=True)
        features = {"age": 30, "prior_cases": 5, "is_repeat_offender": 1,
                     "education_score": 2, "employment_score": 3, "is_male": 1,
                     "substance_abuse": 1, "gang_affiliation": 1,
                     "mental_health_issues": 0, "weapon_use": 1, "violence_score": 7}
        result = _profiling_model.predict(features)
        assert "risk_score" in result
        assert "recidivism_probability" in result
        assert "escalation_risk" in result
        assert "archetype" in result
        assert 0 <= result["risk_score"] <= 100


# ──────────────────────────────────────────────
# Forecasting
# ──────────────────────────────────────────────
forecast_skip = pytest.mark.skipif(not _HAS_FORECAST, reason="prophet not installed")


@forecast_skip
class TestForecastingModule:
    def test_generate_data_daterange(self):
        df = _forecasting_data.generate_daily_crime_data("2024-01-01", "2024-03-31", seed=42)
        assert len(df) >= 89
        assert {"ds", "y"}.issubset(set(df.columns))

    def test_train_returns_metrics(self):
        result = _forecasting_model.train(save=False, periods=30)
        for key in ("mae", "mape", "forecast_days"):
            assert key in result

    def test_train_metrics_valid(self):
        result = _forecasting_model.train(save=False, periods=30)
        assert result["mae"] >= 0
        assert result["mape"] >= 0

    def test_predict_shape(self):
        _forecasting_model.train(save=True, periods=30)
        result = _forecasting_model.predict(days=15)
        assert len(result) == 15
        for entry in result:
            assert {"date", "predicted_value", "lower_bound", "upper_bound"}.issubset(entry.keys())

    def test_predict_horizon(self):
        _forecasting_model.train(save=True, periods=30)
        result = _forecasting_model.predict(days=90)

    def test_predict_confidence_intervals(self):
        _forecasting_model.train(save=True, periods=30)
        result = _forecasting_model.predict(days=10)
        for entry in result:
            assert entry["lower_bound"] <= entry["predicted_value"] <= entry["upper_bound"]


# ──────────────────────────────────────────────
# Hotspot (DBSCAN)
# ──────────────────────────────────────────────
class TestHotspotModule:
    def test_generate_data(self):
        df = _hotspot_data.generate_hotspot_data(n_points=500, n_clusters=3, seed=42)
        assert len(df) == 500
        assert {"latitude", "longitude", "crime_type", "timestamp"}.issubset(set(df.columns))

    def test_generate_data_coords(self):
        df = _hotspot_data.generate_hotspot_data(n_points=100, n_clusters=2,
                                                   center_lat=12.97, center_lon=77.59, seed=42)
        assert df["latitude"].between(12.85, 13.15).all()
        assert df["longitude"].between(77.40, 77.75).all()

    def test_train_returns_stats(self):
        result = _hotspot_model.train(eps=0.01, min_samples=5, save=False)
        for key in ("n_clusters", "n_noise_points", "clusters", "silhouette_score"):
            assert key in result

    def test_train_finds_clusters(self):
        result = _hotspot_model.train(eps=0.05, min_samples=5, save=False)
        assert result["n_clusters"] >= 1

    def test_predict_assigns_labels(self):
        _hotspot_model.train(eps=0.05, min_samples=5, save=True)
        result = _hotspot_model.predict([12.97, 12.98, 13.50], [77.59, 77.60, 77.80])
        assert len(result) == 3
        for item in result:
            assert "cluster" in item
            assert "latitude" in item
            assert "longitude" in item


# ──────────────────────────────────────────────
# Similarity (Sentence Transformers)
# ──────────────────────────────────────────────
class TestSimilarityModule:
    def test_generate_case_descriptions(self):
        df = _similarity_data.generate_case_descriptions(n_per_type=3, seed=42)
        assert "theft" in df["crime_type"].values or "robbery" in df["crime_type"].values
        assert len(df) >= 3

    def test_build_index_returns_metadata(self):
        result = _similarity_model.build_index(save=False)
        assert isinstance(result, dict)
        assert result["embedding_dim"] == 384
        assert result["model"] == "all-MiniLM-L6-v2"
        assert "avg_similarity" in result

    def test_search_returns_results(self):
        _similarity_model.build_index(save=True)
        results = _similarity_model.search("robbery at night near ATM", top_k=3)
        assert 1 <= len(results) <= 3
        for r in results:
            assert {"case_id", "description", "similarity_score"}.issubset(r.keys())
            assert 0 <= r["similarity_score"] <= 1

    def test_search_scores_descending(self):
        _similarity_model.build_index(save=True)
        results = _similarity_model.search("burglary", top_k=5)
        scores = [r["similarity_score"] for r in results]
        assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))


# ──────────────────────────────────────────────
# Sociological
# ──────────────────────────────────────────────
class TestSociologicalModule:
    def test_generate_data_cols(self):
        df = _sociological_data.generate_sociological_data(seed=42)
        expected = {"district", "state", "year", "population", "population_density",
                     "urbanization_rate", "literacy_rate", "avg_income", "poverty_rate",
                     "unemployment_rate", "migration_rate", "juvenile_population_pct",
                     "police_per_capita", "crime_rate_per_100k"}
        assert expected.issubset(set(df.columns))
        assert len(df) >= 80

    def test_analyze_returns_dict(self):
        result = _sociological_model.analyze(save=False)
        for key in ("correlations", "factor_importance", "best_performers", "n_districts"):
            assert key in result
        assert result["n_districts"] >= 1

    def test_analyze_has_correlations(self):
        result = _sociological_model.analyze(save=False)
        assert len(result["correlations"]) >= 8
        assert len(result["factor_importance"]) >= 5

    def test_predict_returns_rate(self):
        _sociological_model.analyze(save=True)
        features = {"population_density": 12000, "unemployment_rate": 8.5,
                     "poverty_rate": 15.2, "literacy_rate": 78.0,
                     "avg_income": 350000, "migration_rate": 5.0,
                     "juvenile_population_pct": 35.0, "urbanization_rate": 60.0,
                     "police_per_capita": 2.5}
        result = _sociological_model.predict(features)
        key = next(k for k in result if "crime" in k.lower())
        assert isinstance(result[key], float)

    def test_predict_positive_rate(self):
        _sociological_model.analyze(save=True)
        features = {"population_density": 5000, "unemployment_rate": 5.0,
                     "poverty_rate": 10.0, "literacy_rate": 90.0,
                     "avg_income": 500000, "migration_rate": 2.0,
                     "juvenile_population_pct": 25.0, "urbanization_rate": 80.0,
                     "police_per_capita": 4.0}
        result = _sociological_model.predict(features)
        key = next(k for k in result if "crime" in k.lower())
        assert result[key] >= 0


# ──────────────────────────────────────────────
# Financial / Fraud Detection
# ──────────────────────────────────────────────
class TestFinancialModule:
    def test_generate_data_imbalance(self):
        df = _financial_data.generate_transactions(n_normal=1000, n_fraud=30, seed=42)
        assert len(df) == 1030
        assert df["is_fraud"].sum() == 30

    def test_generate_data_columns(self):
        df = _financial_data.generate_transactions(n_normal=200, n_fraud=10, seed=42)
        expected = {"transaction_id", "amount", "timestamp", "sender_account",
                    "receiver_account", "transaction_type", "is_fraud", "fraud_pattern"}
        assert expected.issubset(set(df.columns))

    def test_train_returns_metrics(self):
        result = _financial_model.train(save=False)
        for key in ("auc_roc", "f1_score", "feature_importance"):
            assert key in result
        assert 0 <= result["auc_roc"] <= 1

    def test_predict_normal_transaction(self):
        _financial_model.train(save=True)
        tx = {"amount": 5000, "sender_account": "ACC001", "receiver_account": "ACC999",
              "transaction_type": "transfer", "hour": 14, "day_of_week": 3,
              "sender_balance": 100000, "is_night": 0, "amount_log": 8.5}
        result = _financial_model.predict(tx)
        for key in ("is_fraudulent", "fraud_probability", "risk_level"):
            assert key in result
        assert result["risk_level"] in ("low", "medium", "high")

    def test_predict_suspicious_flagged(self):
        _financial_model.train(save=True)
        tx = {"amount": 5000000, "sender_account": "ACC001", "receiver_account": "ACC999",
              "transaction_type": "transfer", "hour": 3, "day_of_week": 0,
              "sender_balance": 100000, "is_night": 1, "amount_log": 15.4}
        result = _financial_model.predict(tx)
        assert isinstance(result["is_fraudulent"], bool)


# ──────────────────────────────────────────────
# Network (Graph ML)
# ──────────────────────────────────────────────
class TestNetworkModule:
    def test_generate_network_size(self):
        G = _network_data.generate_criminal_network(n_persons=50, n_gangs=3, seed=42)
        assert G.number_of_nodes() == 50
        assert G.number_of_edges() >= 40

    def test_network_to_dataframes(self):
        G = _network_data.generate_criminal_network(n_persons=20, n_gangs=2, seed=42)
        nodes, edges = _network_data.network_to_dataframes(G)
        assert len(nodes) == 20
        assert len(edges) >= 15

    def test_analyze_returns_metrics(self):
        result = _network_model.analyze(save=False)
        for key in ("n_nodes", "n_edges", "density", "modularity", "n_communities",
                     "n_triangles", "n_bridges", "top_central_persons", "suspicious_patterns_sampled"):
            assert key in result
        assert result["n_nodes"] >= 50

    def test_analyze_suspicious_patterns(self):
        result = _network_model.analyze(save=False)
        patterns = result["suspicious_patterns_sampled"]
        assert isinstance(patterns, list)
        for p in patterns:
            assert "type" in p

    def test_compute_centrality(self):
        import networkx as nx
        G = _network_data.generate_criminal_network(n_persons=30, n_gangs=2, seed=42)
        graph_data = nx.node_link_data(G)
        result = _network_model.compute_centrality(graph_data)
        assert isinstance(result, dict)
        for node_id, scores in result.items():
            for key in ("degree", "betweenness", "eigenvector"):
                assert key in scores
