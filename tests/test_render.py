from sre_node_sentinel.models import Check, Result, Status
from sre_node_sentinel.render import to_json, to_prometheus


def test_prometheus_output_is_one_hot_and_escaped() -> None:
    result = Result(Check('quote"id', "file_mode", "0600"), Status.FAIL, "0644", "fixture")
    output = to_prometheus([result], 'policy"name')
    assert 'check="quote\\"id",status="fail"} 1' in output
    assert 'status="pass"} 0' in output
    assert 'sre_node_sentinel_failed_checks{policy="policy\\"name"} 1' in output


def test_json_output_contains_result_fields() -> None:
    result = Result(Check("mode", "file_mode", "0600"), Status.PASS, "0600", "fixture")
    assert '"status": "pass"' in to_json([result], "baseline")
