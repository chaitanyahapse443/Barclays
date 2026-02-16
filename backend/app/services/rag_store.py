import os
from pathlib import Path
import json
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
except Exception:
    SentenceTransformer = None
    faiss = None


class RAGStore:
    """RAG store using sentence-transformers for embeddings and FAISS for nearest neighbor search.
    Loads textual assets from `vector_store/regulatory_templates` and `vector_store/past_sar_samples`.
    """
    def __init__(self, repo_root=None, embed_model_name='all-MiniLM-L6-v2'):
        self.repo_root = Path(repo_root or os.path.join(os.path.dirname(__file__), '..', '..')).resolve()
        self.templates_dir = self.repo_root / 'vector_store' / 'regulatory_templates'
        self.samples_dir = self.repo_root / 'vector_store' / 'past_sar_samples'
        self.docs = []
        self.names = []
        self.embed_model_name = embed_model_name
        self._model = None
        self._index = None
        self._embeddings = None
        self._build_index()

    def _load_texts(self, folder: Path):
        texts = []
        for p in folder.glob('**/*'):
            if p.is_file() and p.suffix.lower() in ['.txt', '.md', '.json']:
                try:
                    texts.append(p.read_text())
                    self.names.append(str(p.relative_to(self.repo_root)))
                except Exception:
                    continue
        return texts

    def _build_index(self):
        texts = []
        texts += self._load_texts(self.templates_dir)
        texts += self._load_texts(self.samples_dir)
        self.docs = texts
        if not texts:
            return
        if SentenceTransformer is None or faiss is None:
            # fallback: store docs without embeddings
            return
        self._model = SentenceTransformer(self.embed_model_name)
        emb = self._model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        self._embeddings = emb.astype('float32')
        d = self._embeddings.shape[1]
        index = faiss.IndexFlatIP(d)
        faiss.normalize_L2(self._embeddings)
        index.add(self._embeddings)
        self._index = index

    def save_index(self, dir_path: str):
        """Persist FAISS index and metadata to directory."""
        if faiss is None or self._index is None:
            raise RuntimeError("FAISS or index not available")
        p = Path(dir_path)
        p.mkdir(parents=True, exist_ok=True)
        index_path = str(p / 'index.faiss')
        faiss.write_index(self._index, index_path)
        # save metadata
        with open(str(p / 'meta.json'), 'w', encoding='utf-8') as f:
            json.dump({'names': self.names, 'docs': self.docs, 'embed_model_name': self.embed_model_name}, f)
        return {'index_path': index_path, 'meta': str(p / 'meta.json')}

    def load_index(self, dir_path: str):
        """Load FAISS index and metadata from directory."""
        p = Path(dir_path)
        index_path = p / 'index.faiss'
        meta_path = p / 'meta.json'
        if not index_path.exists() or not meta_path.exists():
            raise RuntimeError("Index or metadata not found in path")
        if faiss is None:
            raise RuntimeError('faiss not available')
        idx = faiss.read_index(str(index_path))
        with open(str(meta_path), 'r', encoding='utf-8') as f:
            meta = json.load(f)
        self._index = idx
        self.names = meta.get('names', [])
        self.docs = meta.get('docs', [])
        self.embed_model_name = meta.get('embed_model_name', self.embed_model_name)
        return {'loaded': True, 'count': len(self.docs)}

    def reindex(self):
        """Rebuild index from current documents."""
        self._build_index()
        return {'reindexed': True, 'count': len(self.docs)}

    def query(self, q: str, top_k: int = 3):
        if self._index is None or self._model is None:
            # fallback to simple keyword match if embeddings unavailable
            results = []
            for i, doc in enumerate(self.docs):
                score = float(doc.lower().count(q.lower()))
                results.append({"source": self.names[i] if i < len(self.names) else str(i), "score": score, "text": doc})
            results = sorted(results, key=lambda r: -r['score'])[:top_k]
            return results
        qv = self._model.encode([q], convert_to_numpy=True)
        qv = qv.astype('float32')
        faiss.normalize_L2(qv)
        D, I = self._index.search(qv, top_k)
        out = []
        for score, idx in zip(D[0], I[0]):
            out.append({"source": self.names[idx] if idx < len(self.names) else str(idx), "score": float(score), "text": self.docs[idx]})
        return out


# singleton accessor
_store = None

def get_rag_store():
    global _store
    if _store is None:
        _store = RAGStore()
    return _store
