import tempfile
from pathlib import Path

import streamlit as st

from pipeline.pipeline import run_pipeline


st.set_page_config(
    page_title="Phylogenomics Pipeline",
    page_icon="🧬",
    layout="wide",
)

st.title("🧬 Full Phylogenomic Pipeline")
st.write(
    "Upload a FASTA file to validate sequences, perform multiple "
    "sequence alignment, trim the alignment, construct a phylogenetic "
    "tree, and calculate bootstrap support."
)

uploaded_file = st.file_uploader(
    "Upload FASTA file",
    type=["fasta", "fa", "fas"],
)

bootstrap = st.selectbox(
    "Bootstrap replicates",
    [100, 500, 1000],
    index=2,
)

if uploaded_file and st.button(
    "Run Phylogenomic Pipeline",
    type="primary",
):

    with tempfile.TemporaryDirectory() as temp_dir:

        temp_path = Path(temp_dir)

        input_file = temp_path / uploaded_file.name
        output_dir = temp_path / "results"

        input_file.write_bytes(
            uploaded_file.getvalue()
        )

        with st.spinner(
            "Running phylogenomic analysis..."
        ):

            try:
                result = run_pipeline(
                    str(input_file),
                    str(output_dir),
                    bootstrap=bootstrap,
                )

            except Exception as error:
                st.error(str(error))
                st.stop()

        st.success(
            "Phylogenomic analysis completed successfully!"
        )

        st.subheader("Sequence Statistics")

        st.json(result["stats"])

        st.subheader(
            "Bootstrap-supported Newick Tree"
        )

        tree = Path(
            result["tree"]
        ).read_text(
            encoding="utf-8"
        )

        st.code(
            tree,
            language="text",
        )

        st.download_button(
            label="Download Newick Tree",
            data=tree,
            file_name="phylogeny.treefile",
            mime="text/plain",
        )

else:

    st.info(
        "Upload a FASTA file to begin the analysis."
    )
