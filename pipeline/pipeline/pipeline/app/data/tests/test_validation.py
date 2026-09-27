from pathlib import Path

import pytest

from pipeline.validation import validate_fasta


def test_validate_fasta(tmp_path):
    input_file = tmp_path / "input.fasta"
    output_file = tmp_path / "validated.fasta"

    input_file.write_text(
        ">A\nATGCATGC\n>B\nATGCATGA\n",
        encoding="utf-8",
    )

    stats = validate_fasta(
        str(input_file),
        str(output_file),
    )

    assert stats["sequences"] == 2
    assert stats["minimum_length"] == 8
    assert stats["maximum_length"] == 8
    assert output_file.exists()


def test_empty_fasta(tmp_path):
    input_file = tmp_path / "empty.fasta"
    output_file = tmp_path / "validated.fasta"

    input_file.write_text("", encoding="utf-8")

    with pytest.raises(ValueError):
        validate_fasta(
            str(input_file),
            str(output_file),
        )


def test_invalid_character(tmp_path):
    input_file = tmp_path / "invalid.fasta"
    output_file = tmp_path / "validated.fasta"

    input_file.write_text(
        ">A\nATGCXYZ\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        validate_fasta(
            str(input_file),
            str(output_file),
        )
