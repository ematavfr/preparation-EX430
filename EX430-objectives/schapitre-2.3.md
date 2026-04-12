# 2.3 — Understand CVE Categories

## Catégories de CVE dans RHACS

RHACS classe les CVE en **5 catégories** selon leur source et leur cible :

| Catégorie | Source | Cible |
|---|---|---|
| **Image CVE (OS)** | Packages OS dans l'image (rpm, deb, apk) | Image/conteneur |
| **Image CVE (Language)** | Dépendances langages (pip, npm, maven, go mod, gem) | Image/conteneur |
| **Node CVE** | Packages OS sur le nœud Kubernetes | Nœud |
| **Platform CVE (K8s)** | Kubernetes lui-même | Cluster |
| **Platform CVE (OpenShift)** | OpenShift (OCP) | Cluster |

## Image CVE — OS

Packages système présents dans l'image :
- RPM (RHEL, CentOS, Fedora)
- DEB (Debian, Ubuntu)
- APK (Alpine)

```
Image: ubi9:latest
├── glibc-2.34 → CVE-2023-4911 (Critical, fixable in 2.34-60.el9_2.7)
├── openssl-3.0.7 → CVE-2023-0286 (Important, fixable)
└── ...
```

## Image CVE — Language

Dépendances de code dans l'image :

| Écosystème | Fichiers détectés |
|---|---|
| Python | `requirements.txt`, `Pipfile.lock`, `*.egg-info` |
| Node.js | `package-lock.json`, `yarn.lock`, `node_modules` |
| Java | `*.jar`, `*.war`, `pom.xml` |
| Go | `go.sum`, binaire compilé (symbols) |
| Ruby | `Gemfile.lock` |
| .NET | `*.deps.json` |

## Node CVE

Packages installés sur le nœud (OS du worker/master) :
- Visible dans **Vulnerability Management → Node CVEs**
- Collector remonte les infos depuis le nœud via DaemonSet
- Exemples : CVE dans le kernel, containerd, runc, cri-o

## Platform CVE

CVE affectant la plateforme d'orchestration elle-même :

**Kubernetes CVE :**
- Détecté depuis la version k8s du cluster
- Ex: vulnérabilité dans kube-apiserver, kubelet

**OpenShift CVE :**
- Détecté depuis la version OCP
- Ex: vulnérabilité dans openshift-apiserver, oauth-server

Visible dans **Vulnerability Management → Platform CVEs**

## Fixabilité

| État | Signification |
|---|---|
| `Fixable` | Une version corrigée du package est disponible |
| `Not fixable` | Aucun fix upstream disponible |
| `Deferred` | Intentionnellement ignoré (deferral actif) |
| `False positive` | Marqué comme faux positif |

## Impact sur la remédiation

```bash
# Trouver les images avec des CVE OS critiques et fixables
# UI : Vulnerability Management → Workload CVEs
# Filtres : Severity=Critical, Fixable=Yes, CVE type=Image

# Remédiation : rebuild l'image avec la version du package corrigée
# Ex: FROM ubi9:9.2-696 → FROM ubi9:9.3-latest
```

---

## Résumé pour l'examen

> - **5 catégories** : Image OS, Image Language, Node, Platform K8s, Platform OCP
> - Image OS = packages rpm/deb/apk dans l'image
> - Image Language = dépendances pip/npm/maven/go dans l'image
> - Node CVE = packages du système hôte du nœud (via Collector)
> - Platform CVE = CVE de K8s ou OCP lui-même (détecté par version)
> - Fixable = version corrigée existe → priorité de remédiation
