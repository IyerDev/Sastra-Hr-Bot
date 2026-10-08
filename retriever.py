import os
import re
import json
import math
from collections import Counter

# Light morphological stemmer (matches 'leaves' -> 'leav', 'worked' -> 'work')
def stem(word: str) -> str:
    w = word.lower()
    if w.endswith("ies") and len(w) > 4:
        return w[:-3] + "y"
    if w.endswith("es") and len(w) > 4:
        return w[:-2]
    if w.endswith("s") and not w.endswith("ss") and len(w) > 3:
        return w[:-1]
    if w.endswith("ing") and len(w) > 5:
        return w[:-3]
    if w.endswith("ed") and len(w) > 4:
        return w[:-2]
    return w

def tokenize(text: str):
    if not text:
        return []
    words = re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())
    return [stem(w) for w in words]

class PolicyRetriever:
    """
    BM25 + Heading-Boost Search Engine for Policy Chunks.
    Runs 100% locally and offline.
    """
    def __init__(self, chunks_file="data/chunks.json"):
        if not os.path.exists(chunks_file):
            raise FileNotFoundError(f"Chunks file missing at {chunks_file}. Run chunker.py first!")

        with open(chunks_file, "r", encoding="utf-8") as f:
            self.chunks = json.load(f)

        self.corpus = [tokenize(f"{c['full_heading']} {c['content']}") for c in self.chunks]
        self.heading_tokens = [tokenize(c["full_heading"]) for c in self.chunks]
        self.doc_lens = [len(doc) for doc in self.corpus]
        self.avgdl = (sum(self.doc_lens) / len(self.doc_lens)) if self.doc_lens else 1.0
        n_docs = len(self.corpus)

        # Precompute frequencies & IDF
        df = Counter()
        self.doc_term_freqs = []
        for doc in self.corpus:
            counts = Counter(doc)
            self.doc_term_freqs.append(counts)
            for word in counts.keys():
                df[word] += 1

        self.idf = {
            word: math.log(1.0 + (n_docs - count + 0.5) / (count + 0.5))
            for word, count in df.items()
        }

    def search(self, query_text: str, top_k: int = 3, k1: float = 1.5, b: float = 0.75):
        q_terms = tokenize(query_text)
        if not q_terms:
            return []

        scores = []
        for i in range(len(self.chunks)):
            doc_len = self.doc_lens[i]
            freqs = self.doc_term_freqs[i]
            h_tokens = set(self.heading_tokens[i])

            bm25 = 0.0
            heading_bonus = 0.0

            for term in q_terms:
                if term in freqs:
                    tf = freqs[term]
                    w_idf = self.idf.get(term, 0.0)
                    denom = tf + k1 * (1.0 - b + b * (doc_len / self.avgdl))
                    bm25 += w_idf * (tf * (k1 + 1.0)) / (denom if denom > 0 else 1.0)
                # Give huge 3.5x bonus if the term is in the section title!
                if term in h_tokens:
                    heading_bonus += 3.5

            total_score = bm25 + heading_bonus
            scores.append(total_score)

        # Rank documents by score
        ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)

        results = []
        for idx in ranked_indices[:top_k]:
            if scores[idx] > 0:
                results.append((scores[idx], self.chunks[idx]))
        return results

# Quick test
if __name__ == "__main__":
    retriever = PolicyRetriever()
    test_q = "maternity leave policy for female employees"
    print(f"\n🔍 Testing Search: '{test_q}'")
    print("=" * 60)
    matches = retriever.search(test_q, top_k=2)
    for rank, (score, chunk) in enumerate(matches, 1):
        print(f"[{rank}] Score: {score:.2f} | {chunk['full_heading']}")
        print(f"Excerpt: {chunk['content'][:140]}...\n")