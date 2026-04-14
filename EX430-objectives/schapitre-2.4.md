# 2.4 — Understand the vulnerability deferral process

## Principe

Un **deferral** (report) permet de marquer une CVE comme intentionnellement ignorée pour une durée définie, avec un motif justifié. C'est un workflow avec **demande + approbation**.

## Workflow

```
Analyste → Demande de deferral → Approbateur → Approuvé / Denied
                ↓                                     ↓
         CVE affichée avec            CVE approuvée : retirée de l'onglet "Observed"
         label "Pending exception"    CVE denied : reste visible, label "Pending exception" retiré
```

## Créer une demande de deferral

### Via l'UI

1. **Vulnerability Management → Workload CVEs**
2. Cliquer sur la CVE concernée
3. **Defer CVE** (bouton en haut à droite)
4. Configurer :
   - **Scope** : toutes les images, une image spécifique, tous les déploiements
   - **Duration** : 2 semaines, 30 jours, 90 jours, indéfini
   - **Reason** : Mitigated by other controls / Risk accepted / False positive
   - **Expiry** : date de fin du deferral

### Via l'API

```bash
curl -sk -X POST "$ROX_ENDPOINT/v1/vulnerabilityexceptions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "comment": "Mitigé par WAF, fix planifié Q3",
    "cves": ["CVE-2024-1234"],
    "scope": {"imageScope": {"registry": "quay.io", "remote": "myorg/myapp", "tag": ".*"}},
    "expiryTime": "2026-09-30T00:00:00Z"
  }'
```

## Rôles nécessaires

| Action | Rôle minimum |
|---|---|
| Demander un deferral | `Vulnerability Management Requester` |
| Approuver/Rejeter | `Vulnerability Management Approver` |
| Les deux | `Vulnerability Management Admin` ou `Admin` |

## États d'une exception

| État | Description |
|---|---|
| `PENDING` | Demande en attente — CVE reste visible avec label "Pending exception" |
| `APPROVED` | Approuvée — CVE retirée de l'onglet **Observed**, masquée des alertes actives |
| `DENIED` | Refusée — CVE redevient pleinement visible (terminologie DO430 : "denied", pas "rejected") |
| `EXPIRED` | Durée écoulée — CVE redevient active automatiquement |

## Gérer les deferrals

UI : **Vulnerability Management → Exception Management**

- Voir toutes les demandes (pending, approved, expired)
- Approuver/rejeter en lot
- Prolonger un deferral existant
- Révoquer une exception approuvée

## Impact sur les policies

Une CVE déférée est **exclue** de l'évaluation des policies de vulnérabilité. Elle n'apparaît plus dans :
- Les violations actives
- Les rapports (sauf si option "include deferred" cochée)
- Les scores de risque des déploiements

## False positive

Même workflow, mais le motif est `False positive` :
- La CVE est marquée comme ne s'appliquant pas réellement
- Exemples : code vulnérable jamais exécuté, package présent mais non utilisé

Consulter les CVEs déférées et false positives approuvées :
**Vulnerability Management → Workload CVEs → onglet Deferred** ou **onglet False positives**

## Snooze — Platform et Node CVEs (mécanisme distinct)

Le **snooze** s'applique aux CVEs **platform** et **node** (pas workload). Différence clé avec le deferral :

| | Deferral (workload) | Snooze (platform/node) |
|---|---|---|
| Approbation requise | Oui (2 rôles) | **Non** — effet immédiat |
| Durées | 2s / 30j / 90j / indéfini | 1j / 1 sem / 2 sem / 1 mois / indéfini |
| Activation | Activée par défaut | **Non activée par défaut** (UI et API) |
| Portée | Images / déploiements | Nœuds / plateforme |

> **Point clé examen** : le snooze platform/node est **désactivé par défaut** dans le portail et l'API — il faut l'activer explicitement avant de pouvoir l'utiliser.

---

## Résumé pour l'examen

> - Deferral = workflow **request → approve** (2 rôles distincts)
> - Scope configurable : toute image, une image/tag précis, un déploiement
> - Durée : limitée (2s, 30j, 90j) ou indéfinie
> - Voir et gérer : **Vulnerability Management → Exception Management**
> - CVE déférée = exclue des policies ET des rapports (sauf option explicite)
> - 3 raisons possibles : Mitigated / Risk accepted / False positive
> - **Snooze** (platform/node CVEs) = pas d'approbation, effet immédiat, **désactivé par défaut**
> - Durées snooze : 1j / 1 sem / 2 sem / 1 mois / indéfini
