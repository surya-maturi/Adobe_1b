import os
import re
import json
import numpy as np
import pdfplumber
from pathlib import Path
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer

def dedupe_chars(text):
    return re.sub(r'([A-Za-z])\1{2,}', r'\1', text)

def clean_line(text):
    text = dedupe_chars(text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_lines(words, y_tol=2):
    from collections import defaultdict
    lines = defaultdict(list)
    for w in words:
        y_key = round(w['top'] / y_tol)
        lines[(w['page_num'], y_key)].append(w)
    merged = []
    for (page_num, _), line_words in lines.items():
        line_words = sorted(line_words, key=lambda w: w['x0'])
        text = ' '.join(w['text'] for w in line_words)
        avg_size = sum(w['size'] for w in line_words) / len(line_words)
        merged.append({"text": clean_line(text), "size": avg_size, "y0": min(w['top'] for w in line_words), "page": page_num})
    return merged

def merge_multiline_headings(headings):
    merged, skip = [], set()
    for i, h in enumerate(headings):
        if i in skip: continue
        ml = h.copy()
        j = i + 1
        while j < len(headings):
            nxt = headings[j]
            if h['page'] == nxt['page'] and abs(nxt['y0'] - ml['y0']) < 20:
                ml['text'] += ' ' + nxt['text']
                skip.add(j)
                j += 1
            else:
                break
        merged.append(ml)
    return merged

def extract_headings(lines):
    candidates = [l for l in lines if len(l['text']) > 8]
    sizes = sorted({round(l['size']) for l in candidates}, reverse=True)
    cluster = []
    for sz in sizes[:4]:
        cluster.extend([l for l in candidates if abs(l['size'] - sz) < 1.5])
    cluster = sorted(cluster, key=lambda l: (l['page'], l['y0']))
    return merge_multiline_headings(cluster)

def extract_sections_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        pages = [p.extract_text() or "" for p in pdf.pages]
        all_lines = []
        for i, page in enumerate(pdf.pages, 1):
            words = page.extract_words(extra_attrs=["size", "top"])
            for w in words: w['page_num'] = i
            all_lines.extend(extract_lines(words))
    headings = extract_headings(all_lines)
    sections = []
    sh = sorted(headings, key=lambda h: (h['page'], h['y0']))
    for idx, h in enumerate(sh):
        title, page = h['text'], h['page']
        body_lines = []
        capturing = False
        for p in range(page, len(pages)+1):
            for line in pages[p-1].split('\n'):
                lc = line.strip()
                if not capturing:
                    if title[:10].lower() in lc.lower():
                        capturing = True
                    continue
                else:
                    if idx+1 < len(sh) and sh[idx+1]['text'][:10].lower() in lc.lower():
                        capturing = False
                        break
                    body_lines.append(lc)
            if not capturing and page != p: break
        body = ' '.join(body_lines).strip()
        if len(body) > 100:
            sections.append({"document": os.path.basename(pdf_path), "section_title": title, "page_number": page, "body": body})
    return sections

def summarize_section(body, persona, job_task, max_chars=600):
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', body) if len(s.strip()) > 10]
    if not sentences:
        return ""
    query = f"{persona} {job_task}"
    tfidf = TfidfVectorizer().fit([query] + sentences)
    s_vecs = tfidf.transform(sentences)
    q_vec = tfidf.transform([query])
    scores = (s_vecs @ q_vec.T).toarray().flatten()
    ranked = [sent for _, sent in sorted(zip(scores, sentences), reverse=True)]
    summary = ""
    for sent in ranked:
        if len(summary) + len(sent) + 1 > max_chars:
            break
        summary += (" " if summary else "") + sent
    return summary

def extract_sections_from_documents(docs, persona, job_task, pdf_dir):
    all_secs = []
    for d in docs:
        path = Path(pdf_dir) / d['filename']
        if path.exists():
            all_secs.extend(extract_sections_from_pdf(path))
    if not all_secs:
        return [], []
    texts = [f"{s['section_title']} {s['body']}" for s in all_secs]
    query = f"{persona} {job_task}"
    tfidf = TfidfVectorizer().fit([query] + texts)
    scores = (tfidf.transform(texts) @ tfidf.transform([query]).T).toarray().flatten()
    idxs = np.argsort(scores)[::-1][:5]
    ext, sub = [], []
    for rank, i in enumerate(idxs, 1):
        s = all_secs[i]
        ext.append({"document": s["document"], "section_title": s["section_title"], "importance_rank": rank, "page_number": s["page_number"]})
        summary = summarize_section(s["body"], persona, job_task)
        sub.append({"document": s["document"], "refined_text": summary, "page_number": s["page_number"]})
    return ext, sub

def process_collection(col_dir):
    in_j = Path(col_dir) / 'challenge1b_input.json'
    out_j = Path(col_dir) / 'challenge1b_output.json'
    pdfd = Path(col_dir) / 'PDFs'
    if not in_j.exists() or not pdfd.exists():
        return
    data = json.loads(in_j.read_text(encoding='utf-8'))
    persona, job = data['persona']['role'], data['job_to_be_done']['task']
    docs = data['documents']
    ext, sub = extract_sections_from_documents(docs, persona, job, pdfd)
    out = {
        "metadata": {
            "input_documents": [d["filename"] for d in docs],
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": datetime.now().isoformat()
        },
        "extracted_sections": ext,
        "subsection_analysis": sub
    }
    out_j.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f"Processed {col_dir}")

def main():
    for sub in Path('.').iterdir():
        if (sub / 'PDFs').exists() and (sub / 'challenge1b_input.json').exists():
            process_collection(sub)

if __name__ == "__main__":
    main()

