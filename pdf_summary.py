"""Summarise a PDF document using the OpenRouter API.

Usage:
    python pdf_summary.py <path-to-pdf>

The program extracts text from the PDF page by page, labels each page with
[Page X] citations, and asks google/gemma-4-26b-a4b-it:free to produce a
structured summary with Overview, Key Points, and Limitations sections.
"""

import argparse
import os
import sys

import fitz
from dotenv import load_dotenv
from openai import OpenAI


# ---------------------------------------------------------------------------
# PDF path validation
# ---------------------------------------------------------------------------

def validate_pdf_path(path):
    """Check that *path* points to a readable PDF file.

    Validates existence, extension, and readability before the program
    touches the API key or initialises the OpenAI client.

    Args:
        path: Filesystem path supplied by the user.

    Returns:
        The normalised *path* string (unchanged, but returned so the caller
        can store it if desired).

    Exits the program early with a friendly message when validation fails.
    """
    if not os.path.isfile(path):
        print(f"Error: file not found — '{path}'")
        raise SystemExit(1)

    if not path.lower().endswith(".pdf"):
        print(f"Error: not a PDF file — '{path}'")
        raise SystemExit(1)

    # Confirm the file can actually be opened for reading.
    try:
        with open(path, "rb"):
            pass
    except PermissionError:
        print(f"Error: permission denied — '{path}'")
        raise SystemExit(1)
    except OSError as e:
        print(f"Error: cannot read file — {e}")
        raise SystemExit(1)

    return path


# ---------------------------------------------------------------------------
# PDF text extraction (PyMuPDF / fitz)
# ---------------------------------------------------------------------------

def extract_pages(path):
    """Extract text from every page of a PDF.

    Opens the PDF with PyMuPDF, iterates pages 1-indexed, and collects
    non-empty text. Pages whose stripped text is empty are silently skipped.

    Args:
        path: Path to a validated PDF file.

    Returns:
        A list of (page_number, text) tuples.  page_number is 1-indexed.
        Returns an empty list when every page is blank or image-only.
    """
    pages = []
    try:
        doc = fitz.open(path)
    except Exception as e:
        print(f"Error: cannot open PDF — {e}")
        raise SystemExit(1)

    total = len(doc)
    for page_index, page in enumerate(doc, start=1):
        print(f"Extracting page {page_index} of {total}...")
        raw = page.get_text()
        cleaned = raw.strip()
        if cleaned:
            pages.append((page_index, cleaned))

    doc.close()
    return pages


def format_pages(pages):
    """Format extracted pages into a single string with [Page X] labels.

    Args:
        pages: List of (page_number, text) tuples from extract_pages().

    Returns:
        A string where each page's content is prefixed with [Page X]
        on its own line, separated by blank lines.
    """
    blocks = []
    for page_num, text in pages:
        blocks.append(f"[Page {page_num}]\n{text}")
    return "\n\n".join(blocks)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------

def load_api_key():
    """Load OPENROUTER_API_KEY from .env and return it.

    Exits the program if the key is missing or empty.
    """
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        print(
            "OPENROUTER_API_KEY is missing. "
            "Add it to .env and try again."
        )
        raise SystemExit(1)

    return api_key


def build_system_prompt(formatted_text):
    """Build the system prompt that instructs the model how to summarise.

    Args:
        formatted_text: Output of format_pages().

    Returns:
        A string containing the full system prompt with embedded document.
    """
    instructions = (
        "You are a document summarisation assistant. "
        "Summarise the content provided below. "
        "Your response MUST include exactly three sections:\n\n"
        "Overview\n"
        "Key Points\n"
        "Limitations\n\n"
        "Every claim you make must include at least one citation "
        "in the format [Page X] where X is the page number. "
        "If the provided text does not contain enough information "
        'for any section, write "Not enough information." under '
        "that section.\n\n"
        f"{formatted_text}"
    )
    return instructions


def summarise(formatted_text, api_key):
    """Send the document to OpenRouter and return the summary.

    Args:
        formatted_text: Output of format_pages().
        api_key: OpenRouter API key loaded from .env.

    Returns:
        The model's summary as a string, or None if an API error occurs.
    """
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = build_system_prompt(formatted_text)

    try:
        response = client.chat.completions.create(
            model="google/gemma-4-26b-a4b-it:free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Summarise the document above."},
            ],
            temperature=0,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error: API request failed — {e}")
        return None


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    """Run the PDF summarisation tool."""
    parser = argparse.ArgumentParser(
        description="Summarise a PDF document using AI."
    )
    parser.add_argument(
        "path",
        help="Path to the PDF file to summarise.",
    )
    args = parser.parse_args()

    # Step 1 — Validate the PDF path (before touching the API key).
    validate_pdf_path(args.path)

    # Step 2 — Extract text page by page.
    pages = extract_pages(args.path)

    # Step 3 — Guard: do not call the API when there is nothing to summarise.
    if not pages:
        print(
            "The PDF contains no extractable text "
            "(all pages may be images or blank)."
        )
        return

    # Step 4 — Format pages with [Page X] labels.
    formatted_text = format_pages(pages)

    # Step 5 — Load the API key (only now, after the PDF is confirmed valid).
    api_key = load_api_key()

    # Step 6 — Send to the OpenRouter API.
    summary = summarise(formatted_text, api_key)

    # Step 7 — Print the result.
    if summary:
        print("\n" + summary)
    else:
        # Error message already printed by summarise().
        raise SystemExit(1)


if __name__ == "__main__":
    main()
