# Préparation EX430 — Red Hat Advanced Cluster Security (RHACS)

Préparation à la certification **Red Hat Certified Specialist in OpenShift Advanced Cluster Security (EX430)**.

## Structure du dépôt

```
preparation-EX430/
├── EX430-objectives/          # Fiches de révision par objectif d'examen
│   ├── objectives.txt         # Liste complète des objectifs EX430
│   ├── schapitre-1.x.md       # Section 1 : Architecture RHACS
│   ├── schapitre-2.x.md       # Section 2 : Gestion des vulnérabilités
│   ├── schapitre-3.x.md       # Section 3 : Policies
│   ├── schapitre-4.x.md       # Section 4 : Segmentation réseau
│   ├── schapitre-5.x.md       # Section 5 : Compliance
│   └── schapitre-6.x.md       # Section 6 : Intégrations tierces
├── diagrammes-app/            # Application web de visualisation
│   ├── html/                  # Diagrammes interactifs (HTML/Mermaid)
│   └── Dockerfile             # Image pour servir les diagrammes localement
├── diagrammes/                # Diagrammes statiques
├── ingest.py                  # Script d'ingestion PDF → Pinecone
├── CLAUDE.md                  # Instructions pour Claude Code
└── .gitignore
```

## Sections de l'examen

| Section | Thème |
|---------|-------|
| 1 | Import secured clusters into RHACS (architecture, opérateurs, Central, SecuredCluster) |
| 2 | Manage Vulnerabilities (scanning, CVE, deferral, rapports, risk) |
| 3 | Manage Policies (violations, admission controller, deploy-time, runtime) |
| 4 | Manage network segmentation (network graph, baselines, network policies) |
| 5 | Manage compliance (Compliance Operator, rapports, tailored profiles) |
| 6 | Third-party integrations (registres, OIDC, object storage, backup/restore) |

## Base de connaissances Pinecone

Le script `ingest.py` indexe les PDFs de documentation RHACS dans un index Pinecone (`rhacs-knowledge-base`) pour permettre la recherche sémantique lors des sessions de révision.

**Prérequis :**
```bash
pip install pinecone pdfplumber
export PINECONE_API_KEY=<votre-clé>
python ingest.py
```

> Les PDFs source (DO430, documentation officielle RHACS) ne sont pas inclus dans ce dépôt.

## Diagrammes interactifs

```bash
# Servir les diagrammes localement
cd diagrammes-app
docker build -t rhacs-diagrammes .
docker run -p 8080:80 rhacs-diagrammes
# Ouvrir http://localhost:8080
```

## Outils utilisés

- **roxctl** — CLI RHACS
- **oc** — CLI OpenShift
- **RHACS Console** — UI web Central
- **Compliance Operator** — gestion compliance OCP
