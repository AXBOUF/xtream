# Weekly Excel Normalization Workflow

This repository contains a notebook-driven workflow to load a weekly Excel workbook (`data/sample.xlsx`), split each weekday sheet into labeled parts using `iloc` slices, clean the parts, merge them into a single normalized DataFrame, and export the result.

Requirements
- Python 3.8+
- A virtual environment (recommended)
- Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you don't have `requirements.txt`, install directly:

```bash
pip install pandas openpyxl numpy
```

How to run
1. Open `notebooks/week.ipynb` in Jupyter or VS Code.
2. Ensure `data/sample.xlsx` exists.
3. Run cells in order. Key sections:
   - Loading: reads sheets into `df_mon` .. `df_sun`.
   - Split: defines `iloc_ranges` and creates `df_<day>_partN` variables.
   - Clean: removes header-rows leaked into parts and drops empty Docket No rows.
   - Merge & Export: concatenates parts into `df_all` and writes `data/sample_cleaned.xlsx`.

Notes
- Adjust `header` and `iloc_ranges` to match your file's layout.
- The notebook prints summary information (rows/cols per part) for verification.

Contact
- If you want me to run the notebook cells here, I can install dependencies and execute the key cells on request.
