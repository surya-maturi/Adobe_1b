**Adobe Challenge 1B: Persona-Driven Document Intelligence**

**Overview**

This solution extracts and prioritizes the most relevant sections from a collection of PDFs, tailored to a given persona and their job-to-be-done. The system is fully offline, CPU-only, under 200MB, and does not use any internet access or file-specific logic. Output is ranked and summarized to align with the sample challenge1b_output.json schema.

**Features**

Persona-aware content extraction: Aligns all section and summary output to the persona and their goal/task.

Generic & robust: Handles any PDF domain—travel, recipes, business reports, etc.

Offline & fast: All code and models run under 60 seconds for typical use cases, with no internet required.

TF-IDF relevance ranking: Ensures only the most relevant content is selected and output.

Output schema: Matches Adobe’s required challenge1b_output.json format, with full metadata, section ranking, and concise summaries.

**Directory Structure**

1b/
 ├─ Collection 1/
 │   ├─ PDFs/
 │   ├─ challenge1b_input.json
 │   └─ challenge1b_output.json
 ├─ Collection 2/
 │   ├─ PDFs/
 │   ├─ challenge1b_input.json
 │   └─ challenge1b_output.json
 ├─ Collection 3/
 │   ├─ PDFs/
 │   ├─ challenge1b_input.json
 │   └─ challenge1b_output.json
run_collections.py
requirements.txt

**Requirements**

Python 3.9+

pdfplumber

scikit-learn

numpy

All are installed via pip and included in the provided Dockerfile.

**How to Run Locally**

pip install pdfplumber scikit-learn numpy
python run_collections.py

All outputs will be saved as challenge1b_output.json in each collection folder.

How to Run with Docker

Build the image:

docker build -t pdf-intel .

**Run:**

docker run --rm -v $PWD:/app pdf-intel


**Output Format**

Each challenge1b_output.json will include:

Metadata (documents, persona, job to be done, timestamp)

Top 5 relevant sections (with titles, document source, page, importance rank)

Concise summaries (subsection_analysis) per selected section

**Notes & Troubleshooting**

Make sure your directory structure matches the above.

The system will skip files or collections if required PDFs or input JSONs are missing.

All section extraction and summarization is done generically—no hardcoded rules per file.
