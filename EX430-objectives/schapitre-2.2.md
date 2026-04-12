# 2.2 — Detect Common Vulnerabilities and Exposures (CVE)

## Vulnerability Management dans l'UI

Navigation : **Vulnerability Management** (menu principal)

### Vues principales

| Vue | Contenu |
|---|---|
| **Workload CVEs** | CVE dans les images des workloads actifs |
| **Node CVEs** | CVE dans les packages des nœuds |
| **Platform CVEs** | CVE Kubernetes/OpenShift |
| **Images** | Liste des images scannées + nb CVE |
| **Deployments** | Déploiements + CVE associés |
| **Components** | Packages/librairies vulnérables |

### Filtres disponibles

- Par sévérité : `Critical`, `Important`, `Moderate`, `Low`
- Par fixabilité : `Fixable`, `Not fixable`
- Par namespace, cluster, déploiement
- Par CVE ID (ex: `CVE-2024-1234`)
- Par composant / package name

## Détecter une CVE spécifique

### Via l'UI

1. **Vulnerability Management → Workload CVEs**
2. Filtre : CVE ID ou nom de composant
3. Voir les images/déploiements affectés

### Via roxctl

```bash
# Scanner une image et filtrer les résultats
roxctl image scan --image=registry.io/image:tag \
  -e $ROX_ENDPOINT \
  --output=json | jq '.result.summary'

# Vérifier une image contre les policies
roxctl image check --image=registry.io/image:tag \
  -e $ROX_ENDPOINT \
  --output=table
```

### Via l'API REST

```bash
# Rechercher une CVE dans l'API
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$ROX_ENDPOINT/v1/cves?query=CVE:CVE-2024-1234" | jq .
```

## Informations disponibles par CVE

| Champ | Description |
|---|---|
| **CVE ID** | Identifiant unique (ex: CVE-2024-21626) |
| **CVSS v3 score** | 0.0 - 10.0 |
| **Sévérité RHACS** | Critical / Important / Moderate / Low |
| **Fixable** | Version corrigée disponible ou non |
| **Fixed in** | Version du package corrigeant la CVE |
| **Summary** | Description de la vulnérabilité |
| **Affected images** | Nombre d'images concernées |
| **Affected deployments** | Nombre de workloads actifs concernés |

## Flux de détection automatique

1. Image poussée dans le registry → scan déclenché (si intégration registry active)
2. Déploiement créé sur cluster sécurisé → scan de l'image + évaluation policies
3. Mise à jour base CVE → re-évaluation automatique des images déjà scannées
4. Si policy `Enforce` → violation créée, potentiellement workload bloqué

## Watchlist (surveillance continue)

Fonctionnalité **CVE Watchlist** :
- Suivre des CVE spécifiques
- Recevoir une notification dès qu'une image affectée apparaît
- UI : **Vulnerability Management → Workload CVEs → [CVE] → Add to watchlist**

---

## Résumé pour l'examen

> - Vue principale : **Vulnerability Management → Workload CVEs**
> - Filtres clés : sévérité, fixabilité, namespace, CVE ID
> - `roxctl image scan` → résultat brut JSON ; `roxctl image check` → évaluation policies
> - RHACS distingue `Critical/Important/Moderate/Low` (mapping depuis CVSS NVD)
> - CVE Watchlist = alerte continue sur une CVE précise
