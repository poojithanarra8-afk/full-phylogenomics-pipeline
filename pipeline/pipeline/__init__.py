from pathlib import Path
from Bio import SeqIO

VALID_DNA = set("ACGTUNRYKMSWBDHV-")


def validate_fasta(input_path: str, output_path: str) -> dict:
    records = list(SeqIO.parse(input_path, "fasta"))

    if not records:
        raise ValueError("No FASTA sequences were found.")

    ids = [record.id for record in records]

    if len(ids) != len(set(ids)):
        raise ValueError("FASTA sequence identifiers must be unique.")

    for record in records:
        sequence = str(record.seq).upper().replace(" ", "")

        if not sequence:
            raise ValueError(f"Sequence {record.id} is empty.")

        invalid = sorted(set(sequence) - VALID_DNA)

        if invalid:
            raise ValueError(
                f"Sequence {record.id} contains invalid characters: "
                f"{', '.join(invalid)}"
            )

        record.seq = record.seq.upper()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    SeqIO.write(records, output_path, "fasta")

    lengths = [len(record.seq) for record in records]

    return {
        "sequences": len(records),
        "minimum_length": min(lengths),
        "maximum_length": max(lengths),
        "average_length": sum(lengths) / len(lengths),
    }
