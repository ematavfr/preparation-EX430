# 2.5 — Generate vulnerability reports

## Types de rapports de vulnérabilité

RHACS propose deux mécanismes :

1. **Vulnerability Reports** (planifiables, par email)
2. **Export CSV/JSON** (ad hoc depuis l'UI)

## Créer un rapport de vulnérabilité planifié

### Via l'UI

1. **Vulnerability Management → Reporting → Create report**
2. Configurer :

| Paramètre | Valeur exemple |
|---|---|
| **Name** | `rapport-critique-hebdo` |
| **Description** | Rapport CVE critiques, fixables |
| **CVE severity** | Critical, Important |
| **Fixability** | Fixable only |
| **CVE status** | Observed (exclut les deferrals) |
| **Image type** | Deployed images |
| **Schedule** | Weekly, Monday 08:00 |
| **Delivery** | Email : ops-security@company.com |
| **Notifier** | Intégration email configurée |

3. **Save** → le rapport s'exécute au schedule défini

### Champs de scope optionnels

- **Collections** : restreindre à un ensemble de clusters/namespaces/deployments
- **Access scope** : limiter aux ressources accessibles par le rôle

## Déclencher un rapport manuellement

```bash
# Via UI : Actions → Send report now
# Via API :
curl -sk -X POST "$ROX_ENDPOINT/v1/report/run" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"reportConfigId": "<config-id>"}'
```

## Export ad hoc (CSV)

UI : **Vulnerability Management → Workload CVEs → Export**

- Format : CSV avec colonnes CVE, sévérité, CVSS, composant, image, déploiement, namespace
- Filtres appliqués avant l'export

```bash
# Via API
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$ROX_ENDPOINT/v1/export/csv/vulnerability-reports" \
  --output vulns.csv
```

## Collections

Les **collections** permettent de cibler des sous-ensembles de ressources pour les rapports :

```bash
# UI : Platform Configuration → Collections
# Définir un selector par :
# - Cluster name
# - Namespace (regex ou exact)
# - Deployment name (regex)
# - Label selector
```

Exemple de collection "Production" : tous les namespaces matchant `prod-.*` sur le cluster `ocp-prod`.

## Format du rapport email

Le rapport envoyé par email contient :
- Résumé : nombre de CVE par sévérité
- Tableau des CVE avec : ID, score CVSS, composant, image, namespace, déploiement, fixabilité
- Lien vers la console RHACS pour les détails

## Rapport d'une image spécifique

```bash
roxctl image scan --image=registry.io/image:tag \
  -e $ROX_ENDPOINT \
  --output=json > scan-result.json

# Ou format table
roxctl image scan --image=registry.io/image:tag \
  -e $ROX_ENDPOINT \
  --output=table
```

---

## Résumé pour l'examen

> - Rapports planifiés : **Vulnerability Management → Reporting**
> - Filtres : sévérité, fixabilité, type d'image, status (observed/deferred)
> - Collections = scope des ressources ciblées par le rapport
> - Envoi par email via un notifier configuré
> - Export CSV ad hoc disponible depuis la vue CVE
> - `roxctl image scan` pour un rapport sur une image spécifique
