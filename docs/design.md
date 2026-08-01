# SmartLearn Agent — Product Design

## Product Goal

SmartLearn Agent helps students understand PDF learning materials by generating summaries, answering questions, and showing clear source citations.

## User Stories

1. As a student, I want to upload a PDF and receive a concise summary, so that I can understand the main ideas quickly.

2. As a student, I want to ask questions about a PDF, so that I can clarify difficult concepts without reading the entire document again.

3. As a student, I want answers to include page citations, so that I can verify the information in the original document.

## Feature List

| Priority | Feature | Timeline |
|---|---|---|
| P0 | Extract readable text from PDF files | Day 2 |
| P0 | Generate structured PDF summaries | Day 2 |
| P0 | Answer questions using PDF content | Day 2 |
| P0 | Include page citations in answers | Day 2 |
| P1 | Split long documents into chunks | Day 3 |
| P1 | Generate embeddings for document chunks | Day 3 |
| P1 | Retrieve relevant chunks before answering | Day 3 |
| P1 | Support multi-turn document Q&A | Day 3 |
| P2 | Save previous questions and answers | Future |
| P2 | Provide a graphical user interface | Future |

## What We Will NOT Build

The initial version will not include:

- User accounts or authentication
- Payment processing
- Cloud file storage
- Collaborative document editing
- OCR for scanned PDFs
- Mobile applications
- Support for every document format
- Production-scale deployment

These features are excluded to keep the initial project focused, testable, and suitable for a short workshop.

## Data Flow

### Day 2: Simple Mode

```text
PDF
→ Extract text page by page
→ Add page labels
→ Append the user's question
→ Send the prompt to the LLM
→ Generate an answer
→ Display the answer with [Page X] citations
