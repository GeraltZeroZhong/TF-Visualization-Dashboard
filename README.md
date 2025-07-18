# TF-Visualization-Dashboard
An interactive dashboard for visualizing transcription factor (TF) data using Dash and Plotly.

# Transcription Factor Analysis Toolkit

This toolkit provides an end-to-end pipeline for processing, annotating, and visualizing transcription factor (TF) binding data. It includes three Python scripts:

- `Interested_fragments.py`: Extracts and aligns binding site sequences from annotated TF data.
- `Regulation.py`: Annotates regulatory modes (activation/repression) using TRRUST database.
- `tfweb.py`: Launches an interactive web visualization interface using Dash.

---

## 🔧 Requirements

- Python 3.8+
- Required packages:

```bash
pip install pandas biopython dash plotly openpyxl
```

---

## File Descriptions

### `Interested_fragments.py` — Sequence Alignment and Output Generation

**Purpose:**  
Processes a TF binding site Excel file, corrects sequence orientation based on strand, generates extracted sequences within a user-defined genomic region, and outputs a cleaned Excel file and FASTA-like TXT file of unique alignments.

**Inputs:**

- `annotated_tf_list.xlsx`: Excel file containing:
  - `TF`, `Source`, `Start`, `Stop`, `Pvalue`, `Strand`, `Mached Sequence`
- User-defined region (`user_start`, `user_stop`) entered interactively

**Outputs:**

- `processed_output.xlsx`: Excel with `SEQ` and `alignment` columns
- `alignment_output.txt`: FASTA-format unique alignments

**Usage:**

```bash
python Interested_fragments.py
```

You will be prompted to input the genomic region of interest (start and stop).

---

### `Regulation.py` — Regulatory Mode Annotation

**Purpose:**  
Annotates each TF in the input list with a regulatory mode based on the TRRUST human dataset.

**Inputs:**

- `prmt3.xlsx`: Excel file with a `TF` column
- `trrust_rawdata.human.tsv`: TRRUST database file (TSV format)

**Output:**

- `annotated_tf_list.xlsx`: Annotated file with an additional column: `调控模式` (`activation`, `repression`, `activation & repression`, or `缺乏证据`)

**Usage:**

```bash
python Regulation.py
```

---

### `tfweb.py` — Interactive Visualization Dashboard

**Purpose:**  
Provides a Dash-based web UI to explore TF binding site intervals and regulatory annotations.

**Features:**

- TF name search (supports fuzzy match)
- Filter by regulatory mode (`activation`, `repression`, `其他`)
- P-value range slider
- Tracks layout to prevent overlap
- Hover tooltips for all TF regions

**Input:**

- `annotated_tf_list.xlsx`: The file produced by `Regulation.py`, must include `TF`, `Start`, `Stop`, `Pvalue`, and `调控模式` columns.

**Usage:**

```bash
python tfweb.py
```

The app will launch at: `http://127.0.0.1:8050/`

---

## Recommended Workflow

1. **Annotate** TF regulatory modes:
   ```bash
   python Regulation.py
   ```

2. **Extract** aligned TF binding sequences in a given region:
   ```bash
   python Interested_fragments.py
   ```

3. **Visualize** annotated TF regions:
   ```bash
   python tfweb.py
   ```

---

## Notes

- Ensure column names in your Excel files match exactly as expected.
- `Mached Sequence` should contain raw sequences (strand-specific).
- The region in `Interested_fragments.py` must be manually entered via prompt.
- `调控模式` is expected to be in Chinese for `tfweb.py` to parse it properly.

---

## File Outputs Summary

| Script                   | Output File               | Format           |
|--------------------------|---------------------------|------------------|
| Regulation.py            | annotated_tf_list.xlsx    | Excel            |
| Interested_fragments.py  | processed_output.xlsx     | Excel            |
|                          | alignment_output.txt      | FASTA (TXT)      |
| tfweb.py                 | — (visual only)           | Dash Web App     |

---
