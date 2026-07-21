import pdfplumber
from langchain_core.documents import Document


def table_to_markdown(table: list[list[str | None]]) -> str:
    """
    Convert a raw 2D table (list of rows) into Markdown table text.
    """
    if not table:
        return ""

    cleaned = []
    for row in table:
        if not row:
            continue

        cleaned_row = [str(cell or "").strip() for cell in row]

        if any(cell for cell in cleaned_row):
            cleaned.append(cleaned_row)

    if not cleaned:
        return ""

    header = cleaned[0]
    data_rows = cleaned[1:] if len(cleaned) > 1 else []

    num_cols = len(header)

    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * num_cols) + " |",
    ]

    for row in data_rows:
        padded = row + [""] * (num_cols - len(row))
        lines.append("| " + " | ".join(padded[:num_cols]) + " |")

    return "\n".join(lines)


def extract_tables_from_pdf(pdf_path: str) -> list[Document]:
    """
    Open PDF with pdfplumber, extract all tables, return LangChain Documents.
    """
    documents = []

    with pdfplumber.open(pdf_path) as pdf:
        for page_index, page in enumerate(pdf.pages):
            tables = page.extract_tables()

            for table_index, table in enumerate(tables):
                markdown = table_to_markdown(table)

                if not markdown.strip():
                    continue

                content = (
                    f"Table from page {page_index + 1} "
                    f"(table {table_index + 1}):\n\n{markdown}"
                )

                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "source": pdf_path,
                            "page": page_index,
                            "content_type": "table",
                            "table_index": table_index,
                        },
                    )
                )

    return documents