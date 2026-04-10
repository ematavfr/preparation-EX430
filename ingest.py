#!/usr/bin/env python3
"""
Ingestion du guide DO430 dans Pinecone (index rhacs-knowledge-base).
- Modèle d'embedding intégré Pinecone : llama-text-embed-v2 (1024 dims)
- Chunking par page (~800 chars max par chunk)
- Métadonnées : text, page, source
"""

import os, re, time, uuid
import pdfplumber
from pinecone import Pinecone

PINECONE_KEY = os.environ.get("PINECONE_API_KEY") or open(os.path.expanduser("~/preparation-EX430/pinecone")).read().strip()
INDEX_NAME   = "rhacs-knowledge-base"
PDF_PATH     = "/home/ematav/preparation-EX430/DO430_OpenShift_Advanced_Cluster_Security.pdf"
CHUNK_SIZE   = 800
CHUNK_OVERLAP= 100
BATCH_SIZE   = 90   # max records par upsert (integrated inference)

pc = Pinecone(api_key=PINECONE_KEY)


def create_index():
    existing = [i.name for i in pc.list_indexes()]
    if INDEX_NAME in existing:
        print(f"Index '{INDEX_NAME}' déjà existant.")
        return
    print(f"Création de l'index '{INDEX_NAME}'...")
    pc.create_index_for_model(
        name=INDEX_NAME,
        cloud="aws",
        region="us-east-1",
        embed={
            "model": "llama-text-embed-v2",
            "field_map": {"text": "text"},
        },
    )
    print("Index créé et prêt.")


def chunk_text(text, size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    """Découpe le texte en chunks avec chevauchement."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start += size - overlap
    return [c for c in chunks if len(c) > 80]


def sanitize(text):
    """Supprime les caractères non encodables."""
    return text.encode('utf-8', errors='ignore').decode('utf-8')\
               .encode('ascii', errors='ignore').decode('ascii')


def extract_chunks():
    """Extrait et découpe le texte du PDF par page."""
    chunks = []
    print(f"Lecture du PDF...")
    with pdfplumber.open(PDF_PATH) as pdf:
        total = len(pdf.pages)
        print(f"  {total} pages détectées.")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if not text:
                continue
            text = sanitize(re.sub(r'\s+', ' ', text).strip())
            for chunk in chunk_text(text):
                chunks.append({
                    "text": chunk,
                    "page": i + 1,
                    "source": f"DO430-p{i+1}",
                })
            if (i + 1) % 50 == 0:
                print(f"  Page {i+1}/{total} traitée...")
    print(f"  {len(chunks)} chunks extraits.")
    return chunks


def upsert_chunks(chunks):
    """Upsert par batch dans Pinecone (integrated inference)."""
    index = pc.Index(INDEX_NAME)
    total = len(chunks)
    for i in range(0, total, BATCH_SIZE):
        batch = chunks[i:i + BATCH_SIZE]
        records = [
            {
                "_id": str(uuid.uuid4()),
                "text": c["text"],
                "page": c["page"],
                "source": c["source"],
            }
            for c in batch
        ]
        index.upsert_records(records=records, namespace="__default__")
        print(f"  Batch {i // BATCH_SIZE + 1} upserted ({min(i + BATCH_SIZE, total)}/{total})")
        time.sleep(0.5)
    print("Ingestion terminée.")


def main():
    create_index()
    chunks = extract_chunks()
    print(f"Ingestion de {len(chunks)} chunks dans Pinecone...")
    upsert_chunks(chunks)

    # Vérification
    time.sleep(3)
    stats = pc.Index(INDEX_NAME).describe_index_stats()
    print(f"\nIndex stats : {stats.total_vector_count} vecteurs indexés.")


if __name__ == "__main__":
    main()
