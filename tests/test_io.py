from __future__ import annotations

from runpod_inference_lab.common.io import append_jsonl, file_sha256, read_jsonl, write_jsonl


def test_jsonl_round_trip_skips_blank_lines(tmp_path):
    path = tmp_path / "rows.jsonl"
    path.write_text('{"a": 1}\n\n{"b": 2}\n', encoding="utf-8")

    assert read_jsonl(path) == [{"a": 1}, {"b": 2}]


def test_append_and_write_jsonl(tmp_path):
    path = tmp_path / "nested" / "rows.jsonl"

    write_jsonl(path, [{"a": 1}])
    append_jsonl(path, [{"b": 2}])

    assert read_jsonl(path) == [{"a": 1}, {"b": 2}]
    assert len(file_sha256(path)) == 64
