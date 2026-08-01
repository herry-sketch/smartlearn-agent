# CLI Q&A Tool — Product Requirements Document

## Goal

Build a beginner-friendly command-line question-answering tool named `cli_qa.py`.

The user pastes source text, asks a question, and receives an answer based only on the supplied text. Every supported answer must include paragraph citations.

## Inputs

1. The user pastes one or more paragraphs into the terminal.
2. Paragraphs are separated by blank lines.
3. The user enters `END` on a new line to finish entering the source text.
4. The user then enters one question.

## Outputs

The program prints:

- A concise answer based only on the supplied text.
- One or more citations in the format `[Paragraph X]`.
- An exact refusal when the source text does not contain the answer:

```text
The provided text does not contain enough information to answer this question.
