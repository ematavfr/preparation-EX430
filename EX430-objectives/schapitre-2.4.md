# 2.4 — Understand the vulnerability deferral process

## Principe

Un **deferral** (report) permet de marquer une CVE comme intentionnellement ignorée pour une durée définie, avec un motif justifié. C'est un workflow avec **demande + approbation**.

## Workflow

```
Analyste → Demande de deferral → Approbateur → Approuvé/Rejeté
                                                    ↓
                                              CVE marquée Deferred
                                              (invisible dans les alertes)
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
| `PENDING` | Demande en attente d'approbation |
| `APPROVED` | Approuvée, CVE masquée des alertes actives |
| `REJECTED` | Refusée |
| `EXPIRED` | Durée écoulée, CVE redevient active |

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

---

## Résumé pour l'examen

> - Deferral = workflow **request → approve** (2 rôles distincts)
> - Scope configurable : toute image, une image/tag précis, un déploiement
> - Durée : limitée (2s, 30j, 90j) ou indéfinie
> - Voir et gérer : **Vulnerability Management → Exception Management**
> - CVE déférée = exclue des policies ET des rapports (sauf option explicite)
> - 3 raisons possibles : Mitigated / Risk accepted / False positive
