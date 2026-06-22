"""Graph services tests — analytics, cypher executor, ingestion pipeline."""
import importlib
import pytest
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock


pytestmark = pytest.mark.asyncio

_analytics = importlib.import_module("analytics.graph_analytics")
_cypher_executor = importlib.import_module("cypher.executor")
_base_importer = importlib.import_module("ingestion.base_importer")
_csv_importer = importlib.import_module("ingestion.csv_importer")


class MockRecord:
    def __init__(self, data: dict):
        self._data = data
    def data(self):
        return self._data
    def __getitem__(self, key):
        return self._data[key]
    def get(self, key, default=None):
        return self._data.get(key, default)
    def __contains__(self, key):
        return key in self._data


def make_mock_session(prepared_result=None):
    """Build an async session mock that returns prepared data from run()."""
    session = AsyncMock()
    result = AsyncMock()

    if prepared_result is not None:
        result.data.return_value = prepared_result
    else:
        result.data.return_value = []

    session.run.return_value = result
    session.__aenter__.return_value = session
    session.__aexit__.return_value = None
    return session


def make_mock_driver(prepared_result=None):
    """Build an async driver mock with session context manager support."""
    result = AsyncMock()
    if prepared_result is not None:
        result.data.return_value = prepared_result
        result.single = AsyncMock(return_value=prepared_result[0] if isinstance(prepared_result, list) else prepared_result)
    else:
        result.data.return_value = []
        result.single = AsyncMock(return_value={"count": 0})

    session = AsyncMock()
    session.run.return_value = result
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=None)

    driver = MagicMock()
    driver.session.return_value = session
    driver.close = AsyncMock()
    return driver


# ──────────────────────────────────────────────
# Graph Analytics
# ──────────────────────────────────────────────
class TestGraphAnalytics:
    @pytest.fixture
    def analytics(self):
        ga = object.__new__(_analytics.GraphAnalytics)
        ga._driver = make_mock_driver([{"node": "test", "score": 0.95}])
        yield ga

    async def test_page_rank_returns_list(self, analytics):
        r = await analytics.page_rank(top_n=5)
        assert isinstance(r, list)

    async def test_betweenness_returns_list(self, analytics):
        r = await analytics.betweenness_centrality(top_n=5)
        assert isinstance(r, list)

    async def test_community_detection_lpa_returns_list(self, analytics):
        r = await analytics.community_detection_lpa()
        assert isinstance(r, list)

    async def test_detect_communities_wcc_returns_list(self, analytics):
        r = await analytics.detect_communities_wcc()
        assert isinstance(r, list)

    async def test_shortest_path_returns_list(self, analytics):
        r = await analytics.shortest_path("person-a", "person-b", max_depth=4)
        assert isinstance(r, list)

    async def test_suspicious_patterns(self, analytics):
        r = await analytics.suspicious_patterns()
        assert isinstance(r, dict)
        assert "isolated_persons" in r

    async def test_degree_distribution_returns_dict(self, analytics):
        r = await analytics.degree_distribution()
        assert isinstance(r, list)

    async def test_closing_driver(self, analytics):
        await analytics.close()
        analytics._driver.close.assert_awaited_once()


# ──────────────────────────────────────────────
# Cypher Executor
# ──────────────────────────────────────────────
class TestCypherExecutor:
    @pytest.fixture
    def executor(self):
        ce = object.__new__(_cypher_executor.CypherExecutor)
        ce._driver = make_mock_driver([{"result": "ok"}])
        yield ce

    async def test_run_raw_cypher(self, executor):
        r = await executor.run("MATCH (n) RETURN n LIMIT 1", {})
        assert isinstance(r, list)

    async def test_run_query_lookup(self, executor):
        r = await executor.run_query("criminal", {"person_id": "p1"})
        assert isinstance(r, list)

    async def test_run_query_missing_name(self, executor):
        with pytest.raises(ValueError, match="Unknown query"):
            await executor.run_query("NONEXISTENT_QUERY")

    async def test_execute_transaction(self, executor):
        r = await executor.execute_transaction([("MATCH (n) RETURN n", {})])
        assert isinstance(r, list)
        assert len(r) == 1

    async def test_create_indexes(self, executor):
        await executor.create_indexes()
        assert executor._driver.session.call_count >= 1

    async def test_close(self, executor):
        await executor.close()
        executor._driver.close.assert_awaited_once()


# ──────────────────────────────────────────────
# Ingestion Pipeline
# ──────────────────────────────────────────────
class TestBaseImporter:
    @pytest.fixture
    def importer(self):
        bi = object.__new__(_base_importer.BaseImporter)
        bi._driver = make_mock_driver([{"count": 0}])
        yield bi

    async def test_execute_batch_empty(self, importer):
        c = await importer.execute_batch("CREATE (n:Test)", [])
        assert c == 0

    async def test_execute_batch_with_records(self, importer):
        records = [{"id": "1", "name": "test"}]
        c = await importer.execute_batch(
            "CREATE (n:Test {id: row.id, name: row.name}) RETURN n", records, batch_size=1
        )
        assert c == 1

    async def test_clear_database(self, importer):
        await importer.clear_database()
        importer._driver.session.assert_called()

    async def test_create_constraints(self, importer):
        await importer.create_constraints()
        assert importer._driver.session.call_count >= 1

    async def test_count_nodes(self, importer):
        from unittest.mock import AsyncMock, MagicMock

        records_list = [
            MockRecord({"label": "Person", "count": 100}),
            MockRecord({"label": "Case", "count": 50}),
        ]

        # Build an async iterator that yields MockRecords then stops
        async def _agen():
            for rec in records_list:
                yield rec

        agen = _agen()

        r1 = MagicMock()
        r1.__aiter__ = MagicMock(return_value=agen)

        r2 = MagicMock()
        r2.single = AsyncMock(return_value=MockRecord({"total": 42}))
        r2.data = MagicMock(return_value=[])

        importer._driver.session.return_value.run.side_effect = [r1, r2]
        counts = await importer.count_nodes()
        assert isinstance(counts, dict)
        assert counts.get("Person") == 100
        assert counts.get("Case") == 50
        assert counts.get("_total_relationships") == 42

    async def test_close(self, importer):
        await importer.close()
        importer._driver.close.assert_awaited_once()


class TestCSVImporter:
    @pytest.fixture
    def csv_importer(self, tmp_path):
        import csv
        persons_csv = tmp_path / "persons.csv"
        with open(persons_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "name", "age", "gender", "phone", "address", "district"])
            w.writerow(["P001", "Test Person", "35", "Male", "+919999999999", "Addr", "BN"])

        cases_csv = tmp_path / "cases.csv"
        with open(cases_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "fir_number", "crime_type", "status", "date_occurred",
                        "description", "district", "victim_name", "suspect_name"])
            w.writerow(["C001", "FIR/001", "Theft", "Open", "2024-06-01", "desc", "BN", "V", "S"])

        rels_csv = tmp_path / "relationships.csv"
        with open(rels_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["source_id", "target_id", "type", "weight"])
            w.writerow(["P001", "P002", "KNOWN", "0.8"])

        loc_csv = tmp_path / "locations.csv"
        with open(loc_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "case_id", "latitude", "longitude", "location_type", "district"])
            w.writerow(["L001", "C001", "12.97", "77.59", "crime_scene", "BN"])

        ev_csv = tmp_path / "evidence.csv"
        with open(ev_csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["id", "case_id", "type", "description", "collected_date", "collected_by"])
            w.writerow(["E001", "C001", "Forensic", "Fingerprint", "2024-06-02", "Officer"])

        ci = object.__new__(_csv_importer.CSVImporter)
        ci._driver = make_mock_driver()
        yield ci, str(persons_csv), str(cases_csv), str(rels_csv), str(loc_csv), str(ev_csv)

    async def test_import_persons(self, csv_importer):
        ci, p, _, _, _, _ = csv_importer
        n = await ci.import_persons(p)
        assert n >= 0

    async def test_import_cases(self, csv_importer):
        ci, _, c, _, _, _ = csv_importer
        n = await ci.import_cases(c)
        assert n >= 0

    async def test_import_relationships(self, csv_importer):
        ci, _, _, r, _, _ = csv_importer
        n = await ci.import_relationships(r)
        assert n >= 0

    async def test_full_import_pipeline(self, csv_importer):
        ci, p, c, r, _, _ = csv_importer
        n1 = await ci.import_persons(p)
        n2 = await ci.import_cases(c)
        n3 = await ci.import_relationships(r)
        assert n1 + n2 + n3 >= 0

    async def test_import_locations(self, csv_importer):
        ci, _, _, _, loc_csv, _ = csv_importer
        n = await ci.import_locations(loc_csv)
        assert n >= 0

    async def test_import_evidence(self, csv_importer):
        ci, _, _, _, _, ev_csv = csv_importer
        n = await ci.import_evidence(str(ev_csv))
        assert n >= 0
