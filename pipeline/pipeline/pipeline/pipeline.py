import argparse
import shutil
import subprocess
from pathlib import Path

from .validation import validate_fasta


def run_command(command, log_path):
    if shutil.which(command[0]) is None:
        raise RuntimeError(
            f"Required program '{command[0]}' was not found. "
            "Install it or use Docker."
        )

    with open(log_path, "a", encoding="utf-8") as log:
        log.write("$ " + " ".join(command) + "\n")

        result = subprocess.run(
            command,
            stdout=log,
            stderr=subprocess.STDOUT,
            text=True,
        )

    if result.returncode != 0:
        raise RuntimeError(
            f"Command failed: {' '.join(command)}. "
            f"See {log_path} for details."
        )


def run_pipeline(input_fasta, output_dir, bootstrap=1000, threads="AUTO"):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)

    log = output / "pipeline.log"

    validated = output / "validated.fasta"
    aligned = output / "aligned.fasta"
    trimmed = output / "trimmed.fasta"

    # Step 1: Validate FASTA
    stats = validate_fasta(
        str(input_fasta),
        str(validated)
    )

    log.write_text(
        f"Full Phylogenomic Pipeline\n"
        f"Bootstrap replicates: {bootstrap}\n",
        encoding="utf-8",
    )

    # Step 2: Multiple Sequence Alignment using MAFFT
    if shutil.which("mafft") is None:
        raise RuntimeError(
            "MAFFT was not found. Install MAFFT or use Docker."
        )

    with open(aligned, "w", encoding="utf-8") as handle:
        result = subprocess.run(
            [
                "mafft",
                "--auto",
                str(validated),
            ],
            stdout=handle,
            stderr=subprocess.PIPE,
            text=True,
        )

    if result.returncode != 0:
        raise RuntimeError(
            "MAFFT failed:\n" + result.stderr
        )

    # Step 3: Alignment trimming using trimAl
    run_command(
        [
            "trimal",
            "-in",
            str(aligned),
            "-out",
            str(trimmed),
            "-automated1",
        ],
        log,
    )

    # Step 4: Phylogenetic tree + Bootstrap using IQ-TREE 2
    prefix = output / "phylogeny"

    run_command(
        [
            "iqtree2",
            "-s",
            str(trimmed),
            "-m",
            "MFP",
            "-B",
            str(bootstrap),
            "--alrt",
            "1000",
            "-nt",
            str(threads),
            "-pre",
            str(prefix),
        ],
        log,
    )

    treefile = Path(
        str(prefix) + ".treefile"
    )

    if not treefile.exists():
        raise RuntimeError(
            "IQ-TREE completed but no .treefile was produced."
        )

    return {
        "stats": stats,
        "validated": str(validated),
        "aligned": str(aligned),
        "trimmed": str(trimmed),
        "tree": str(treefile),
        "log": str(log),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Full Phylogenomic Pipeline"
    )

    parser.add_argument(
        "input_fasta"
    )

    parser.add_argument(
        "--output",
        default="results"
    )

    parser.add_argument(
        "--bootstrap",
        type=int,
        default=1000
    )

    parser.add_argument(
        "--threads",
        default="AUTO"
    )

    args = parser.parse_args()

    result = run_pipeline(
        args.input_fasta,
        args.output,
        args.bootstrap,
        args.threads,
    )

    print("Pipeline completed successfully.")
    print(
        "Bootstrap-supported tree:",
        result["tree"]
    )


if __name__ == "__main__":
    main()
