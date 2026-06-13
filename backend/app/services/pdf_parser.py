import pdfplumber
import pandas as pd

try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False


def extract_tables_from_pdf(file_path: str) -> pd.DataFrame:
    """
    Extract tabular data from PDF using pdfplumber.
    Falls back to raw text if no tables exist.
    """

    all_data = []

    with pdfplumber.open(file_path) as pdf:

        for page in pdf.pages:

            table = page.extract_table()

            if table:
                all_data.extend(table)

    if not all_data:

        text_dump = ""

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:
                text_dump += (
                    page.extract_text() or ""
                ) + "\n"

        return pd.DataFrame([
            {
                "raw_text": text_dump
            }
        ])

    headers = all_data[0]

    headers = [
        h if h else f"Col_{i}"
        for i, h in enumerate(headers)
    ]

    rows = all_data[1:]

    cleaned_rows = [
        row
        for row in rows
        if len(row) == len(headers)
    ]

    return pd.DataFrame(
        cleaned_rows,
        columns=headers
    )


def process_pdf(file_path: str) -> pd.DataFrame:
    """
    Main PDF processing function.

    Tries:
    1. Camelot
    2. pdfplumber
    """

    if CAMELOT_AVAILABLE:

        try:

            tables = camelot.read_pdf(
                file_path,
                pages="all",
                flavor="stream"
            )

            if len(tables) > 0:

                return pd.concat(
                    [table.df for table in tables],
                    ignore_index=True
                )

        except Exception:
            pass

    return extract_tables_from_pdf(file_path)