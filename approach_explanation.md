Approach Explanation
1. Overview
Our solution is a persona-driven PDF document intelligence system designed for Challenge 1B. The system ingests a collection of PDFs, a persona description, and a concrete job-to-be-done, then outputs a ranked and summarized list of the most relevant document sections and refined sub-sections, tailored to the persona's intent. The system runs fully offline, CPU-only, and processes up to 10 PDFs in under 60 seconds.

2. Methodology
a. Heading and Section Extraction
Using pdfplumber, we extract all text lines from each PDF with associated font size and page data. Heading candidates are identified by larger font sizes, position, and text length. To prevent fragmented headings and improve context, multi-line headings are merged and deduplicated. Only meaningful, non-repetitive headings are considered to avoid noise.

b. Section Content Association
For each heading, the system captures the subsequent body text (all lines until the next heading or page). Bodies are filtered for substantial content, skipping empty or repetitive sections. This ensures that only relevant, information-rich sections are included.

c. Relevance Ranking (TF-IDF-based)
All candidate sections are ranked using TF-IDF vector similarity against a query combining persona and job-to-be-done. This ensures that only the sections most closely aligned with the task and persona are included in the output. The top 5 sections are selected.

d. Subsection Summarization
For each top section, a concise summary is produced via extractive TF-IDF: the most relevant sentences are selected, capped at a short character limit (e.g., 400–600 chars). This guarantees a non-empty, context-rich summary for each selected section.

e. Output Structure
The output JSON includes required metadata, extracted and ranked sections, and refined sub-sections. All outputs match the expected schema for the Adobe Hackathon.

3. Offline, Fast, Generalizable
Runs Offline: Uses only pdfplumber and scikit-learn (TF-IDF). No APIs, no internet, <200MB installed.

Fast: Processing is linear in the number of sections, and all models are lightweight.

Generic: No file-specific logic, no hardcoded heading strings; all logic is based on document structure, font, and content relevance.

Multilingual Ready: The approach can be extended for non-English PDFs by configuring TfidfVectorizer with additional language support.

4. Strengths & Further Improvements
Strengths:

Robust to noisy headings and extraneous text.

Generic for any document type, persona, or job description.

Highly efficient and simple to deploy offline.

Further Improvements:

Integrate fast, lightweight semantic reranking (sentence transformers) if model size allows.

Add OCR fallback for scanned/image-based PDFs (e.g., Tesseract).

Enhance multi-language support.