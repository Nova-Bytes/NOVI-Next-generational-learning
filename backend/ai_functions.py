import io
import re
from typing import List, Dict
import PyPDF2
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def _split_sentences(text: str) -> List[str]:
    # quick sentence splitter
    sents = re.split(r'(?<=[\.\?\!])\s+', text.strip())
    return [s.strip() for s in sents if len(s.strip()) > 10]

def extract_text_from_file(uploaded_file) -> str:
    fname = uploaded_file.name.lower()
    try:
        if fname.endswith(".pdf"):
            reader = PyPDF2.PdfReader(uploaded_file)
            texts = []
            for p in reader.pages:
                texts.append(p.extract_text() or "")
            return "\n".join(texts)
        elif fname.endswith(".docx"):
            document = docx.Document(uploaded_file)
            return "\n".join([p.text for p in document.paragraphs])
        elif fname.endswith(".txt"):
            uploaded_file.seek(0)
            return uploaded_file.read().decode("utf-8")
    except Exception as e:
        return f"[Error extracting text: {e}]"
    return ""


def summarize_text(text: str, max_sentences: int = 6) -> str:
    if not text:
        return ""
    sents = _split_sentences(text)
    if len(sents) <= max_sentences:
        return "\n".join(sents)
    try:
        vect = TfidfVectorizer(stop_words='english')
        X = vect.fit_transform(sents)
        scores = X.sum(axis=1).A1  
        top_idx = np.argsort(scores)[-max_sentences:]
        top_idx_sorted = sorted(top_idx)
        summary = " ".join([sents[i] for i in top_idx_sorted])
        return summary
    except Exception as e:
        return " ".join(sents[:max_sentences])


def generate_quiz_from_text(text: str, n: int = 3) -> List[Dict]:
    sents = _split_sentences(text)
    if not sents:
        return []
    
    try:
        vect = TfidfVectorizer(stop_words='english')
        X = vect.fit_transform(sents)
        scores = X.sum(axis=1).A1
        top_idx = np.argsort(scores)[-n:]
        qas = []
        for idx in sorted(top_idx, reverse=True):
            s = sents[idx]
            if " is " in s:
                left, right = s.split(" is ", 1)
                question = f"What is {left.strip()}?"
                answer = "is " + right.strip()
            elif " are " in s:
                left, right = s.split(" are ", 1)
                question = f"What are {left.strip()}?"
                answer = "are " + right.strip()
            else:
                # fallback
                question = f"Explain: {s[:80].rstrip()}..."
                answer = s
            qas.append({"question": question, "answer": answer})
        return qas
    except Exception:
        return [{"question": sents[0][:80] + "...", "answer": sents[0]}]


def suggest_focus_sections(text: str, n: int = 5) -> List[str]:
    sents = _split_sentences(text)
    if not sents:
        return []
    try:
        vect = TfidfVectorizer(stop_words='english')
        X = vect.fit_transform(sents)
        scores = X.sum(axis=1).A1
        top_idx = np.argsort(scores)[-n:]
        # return sentences in original order
        return [sents[i] for i in sorted(top_idx)]
    except Exception:
        return sents[:n]


def build_semantic_index(chunks: List[str], model_name: str = "all-MiniLM-L6-v2"):
    from sentence_transformers import SentenceTransformer
    from sklearn.neighbors import NearestNeighbors
    model = SentenceTransformer(model_name)
    embeddings = model.encode(chunks, convert_to_numpy=True)
    nn = NearestNeighbors(n_neighbors=5, metric='cosine').fit(embeddings)
    return {"model": model, "embeddings": embeddings, "nn": nn, "chunks": chunks}

def semantic_search(query: str, index, top_k: int = 3):
    model = index["model"]
    nn = index["nn"]
    embeddings = index["embeddings"]
    chunks = index["chunks"]
    q_emb = model.encode([query], convert_to_numpy=True)
    dists, idxs = nn.kneighbors(q_emb, n_neighbors=top_k)
    results = [{"chunk": chunks[i], "score": float(dists[0][j])} for j, i in enumerate(idxs[0])]
    return results
