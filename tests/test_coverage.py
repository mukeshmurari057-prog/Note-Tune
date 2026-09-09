from backend.app.coverage import check_coverage, parse_concepts


def test_concepts_keep_order_and_coverage_is_reported():
    concepts = parse_concepts("Water is wet. Plants need sunlight!\n- Roots drink water.")
    assert [concept.index for concept in concepts] == [1, 2, 3]
    report = check_coverage(concepts, "Water is wet. Plants need sunlight. Roots drink water.")
    assert report["passed"] is True


def test_missing_detail_fails_coverage():
    concepts = parse_concepts("Mercury is the smallest planet.")
    report = check_coverage(concepts, "Mercury is a planet.")
    assert report["passed"] is False
    assert "smallest" in report["items"][0]["missing_keywords"]

