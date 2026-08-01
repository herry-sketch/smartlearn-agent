import argparse
import os
import re

from dotenv import load_dotenv
from openai import OpenAI


def read_text():
    """Read multiline text from the user until END is entered on its own line.

    Returns:
        The full text as a single string (without the END sentinel).
    """
    print("Paste your source text below.")
    print("Type END on a new line when you are finished.\n")

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            # Handle Ctrl+D gracefully — treat as end of input.
            break
        if line.strip() == "END":
            break
        lines.append(line)

    return "\n".join(lines)


def read_text_from_file(filepath):
    """Read source text from a UTF-8 text file.

    Args:
        filepath: Path to the text file.

    Returns:
        The file contents as a string, or None if the file cannot be read.
        In that case a friendly error message is printed before returning.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: file not found — '{filepath}'")
    except PermissionError:
        print(f"Error: permission denied — '{filepath}'")
    except OSError as e:
        print(f"Error: cannot read file — {e}")
    return None


def split_paragraphs(text):
    """Split text into paragraphs separated by one or more blank lines.

    Blank lines that contain only whitespace (spaces, tabs) are also treated
    as paragraph separators. Uses re.split from the standard library.

    Args:
        text: The raw multiline string from read_text().

    Returns:
        A list of non-empty paragraph strings, with whitespace stripped.
    """
    # Split on sequences of: newline, any whitespace, newline.
    # This handles \n\n, \n   \n, \n\n\n, and any mix of blank lines.
    raw = re.split(r"\n\s*\n", text)
    paragraphs = []
    for p in raw:
        cleaned = p.strip()
        if cleaned:
            paragraphs.append(cleaned)
    return paragraphs


def number_paragraphs(paragraphs):
    """Format paragraphs as a numbered string for the AI prompt.

    Paragraphs are 1-indexed: the first paragraph is Paragraph 1.
    Each paragraph is formatted as [Paragraph X] on its own line,
    followed by the paragraph text.

    Args:
        paragraphs: List of paragraph strings.

    Returns:
        A single string with each paragraph prefixed by its number.
    """
    numbered = ""
    for i, paragraph in enumerate(paragraphs, start=1):
        numbered += f"[Paragraph {i}]\n{paragraph}\n\n"
    return numbered.strip()


def ask_question(numbered_text, question):
    """Send the numbered paragraphs and question to the OpenRouter API.

    Loads the API key from .env, builds a system prompt that instructs the
    model to cite sources and return a sentinel when the text is insufficient,
    then calls the API and returns the answer.

    Args:
        numbered_text: The output of number_paragraphs().
        question: The user's question string.

    Returns:
        The model's answer as a string.
    """
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")

    if not api_key:
        raise SystemExit(
            "OPENROUTER_API_KEY is missing. Add it to .env and try again."
        )

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

    system_prompt = (
        "You are a reading comprehension assistant. "
        "You must answer questions using ONLY the paragraphs provided below. "
        "If the paragraphs do not contain enough information to answer the question, "
        'respond with exactly "INSUFFICIENT_EVIDENCE" and nothing else. '
        "Every supported answer must include at least one citation in the format "
        "[Paragraph X] where X is the paragraph number.\n\n"
        f"{numbered_text}"
    )

    response = client.chat.completions.create(
        model="google/gemma-4-26b-a4b-it:free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=0,
        max_tokens=300,
    )

    return response.choices[0].message.content


def main():
    """Run the interactive CLI Q&A tool."""
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        description="Ask questions about a source text using AI."
    )
    parser.add_argument(
        "--file",
        metavar="PATH",
        help="Read source text from a UTF-8 text file instead of pasting it.",
    )
    args = parser.parse_args()

    # Step 1 — Read source text (from file or interactive input).
    if args.file:
        text = read_text_from_file(args.file)
        if text is None:
            # File could not be read; error already printed by the helper.
            return
    else:
        text = read_text()

    # Step 2 — Split into paragraphs on blank lines.
    paragraphs = split_paragraphs(text)

    # Guard: do not call the API when the source text is empty.
    if not paragraphs:
        print("No source text was provided.")
        return

    # Step 3 — Number paragraphs for the AI prompt.
    numbered_text = number_paragraphs(paragraphs)

    # Step 4 — Read the question.
    question = input("Enter your question: ").strip()

    # Guard: do not call the API when the question is empty.
    if not question:
        print("No question was provided.")
        return

    # Step 5 — Send to the OpenRouter API.
    answer = ask_question(numbered_text, question)

    # Step 6 — If the model signals insufficient evidence, print the exact
    # refusal message from the PRD. Otherwise print the answer.
    if answer and "INSUFFICIENT_EVIDENCE" in answer:
        print(
            "The provided text does not contain enough information "
            "to answer this question."
        )
    else:
        print("\n" + (answer or ""))


if __name__ == "__main__":
    main()
