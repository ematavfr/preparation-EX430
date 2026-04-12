# 2.1 — Manage vulnerability data sources and scanning

## Sources de données CVE

RHACS agrège les données CVE depuis plusieurs sources :

| Source | Données |
|---|---|
| **NVD** (National Vulnerability Database) | CVE base + CVSS scores |
| **Red Hat Security Data** | CVE RHEL/OCP spécifiques + advisories |
| **Alpine SecDB, Debian, Ubuntu** | CVE distro-spécifiques |
| **GitHub Advisory DB** | CVE langages (npm, pip, maven, go...) |
| **OSV** (Open Source Vulnerabilities) | CVE open-source |

Mise à jour automatique si `connectivity: Online` — intervalle : ~1h.

En mode `Offline` : utiliser `roxctl scanner download-db` pour télécharger la base manuellement.

## Types de scan

### 1. Image scanning

Analyse le contenu des images (packages OS + dépendances langages) :

```bash
# Scan CLI
roxctl image scan --image=registry.io/repo/image:tag -e $ROX_ENDPOINT

# Check (scan + évaluation policies)
roxctl image check --image=registry.io/repo/image:tag -e $ROX_ENDPOINT
```

**Déclencheurs automatiques :**
- À chaque push d'image dans un registry intégré
- À chaque déploiement sur un cluster sécurisé
- Périodiquement (re-scan configurable)

### 2. Node scanning

Scan des packages OS installés sur les nœuds Kubernetes :
- Collector remonte les infos au Sensor
- Visible dans UI : **Vulnerability Management → Nodes**

### 3. Platform/Cluster scanning

CVE affectant Kubernetes / OpenShift lui-même :
- Analysé à partir de la version k8s/OCP détectée
- UI : **Vulnerability Management → Platform CVEs**

## Scanner V2 vs Scanner V4

| Critère | Scanner V2 (StackRox) | Scanner V4 (Claircore) |
|---|---|---|
| Moteur | Clair v2 interne | Claircore |
| Langages | Java, Python, Node, Ruby, Go | Idem + meilleure précision |
| Activation | Défaut | Optionnel (CR Central) |
| Architecture | Monolithique | Indexer + Matcher séparés |
| Performance | Standard | Meilleure à grande échelle |

## Configurer le re-scan périodique

UI : **Platform Configuration → System Configuration → Vulnerability Management**

- `Image scan schedule` : intervalle de re-scan des images existantes
- Par défaut : re-scan lors de chaque nouveau déploiement

## Intégration CI/CD

```bash
# Dans une pipeline (Tekton, Jenkins, GitHub Actions...)
roxctl image check \
  --image=$IMAGE \
  --endpoint=$ROX_ENDPOINT \
  --insecure-skip-tls-verify \
  --output=json
```

Retourne un exit code non-nul si une policy en `Enforce` est violée.

---

## Résumé pour l'examen

> - CVE sources : NVD, Red Hat, distros, GitHub Advisory, OSV
> - 3 types de scan : **images**, **nodes**, **platform**
> - Scanner V2 = défaut ; Scanner V4 = Claircore, activé dans la CR Central
> - `roxctl image check` = scan + évaluation policies → utilisé en CI/CD
> - Mode Offline → `roxctl scanner download-db` pour mise à jour manuelle
