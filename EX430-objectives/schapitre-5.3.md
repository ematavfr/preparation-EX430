# 5.3 — Manipulate compliance reports

## Générer un rapport de conformité

### Via l'UI

1. **Compliance → [Standard] → Generate Report**
2. Choisir :
   - Standard(s) à inclure
   - Cluster(s) cible(s)
   - Format : PDF ou CSV
3. **Download** ou **Email** (si notifier configuré)

### Rapport planifié

1. **Compliance → Reporting → Create Schedule**
2. Configurer :
   - Fréquence : Daily / Weekly / Monthly
   - Standards inclus
   - Destinataires (via notifier email)

## Format des rapports

### CSV

Colonnes typiques :

| Colonne | Description |
|---|---|
| Standard | CIS OCP4, NIST 800-53... |
| Control ID | ex: CIS-1.1.1 |
| Control Name | Description du contrôle |
| Status | Pass / Fail / N/A |
| Cluster | Nom du cluster |
| Namespace | Si applicable |
| Resource | Ressource Kubernetes concernée |
| Evidence | Détail technique |

### PDF

Rapport exécutif avec :
- Score global par standard
- Graphiques de répartition Pass/Fail/N/A
- Liste des contrôles en échec avec recommandations

## Export via API

```bash
# Rapport de conformité en JSON via API
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$ROX_ENDPOINT/v1/compliance/results?standard=CIS_Kubernetes_v1_5_1" \
  | jq '.results[] | select(.overallPass == false)'
```

## Rapport depuis le Compliance Operator (OpenSCAP)

```bash
# Les résultats bruts OpenSCAP sont stockés dans un PV
# Récupérer le rapport ARF (Asset Reporting Format) :
oc get pods -n openshift-compliance -l app=ocp4-cis

# Extraire le rapport depuis le pod de résultats
oc cp openshift-compliance/<result-pod>:/reports/0 ./compliance-reports/
```

## Rapport différentiel

Comparer deux runs de scan :

```bash
oc get compliancecheckresults -n openshift-compliance \
  -l compliance.openshift.io/suite=cis-compliance \
  --output=jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.status.result}{"\n"}{end}' \
  | grep FAIL > current-fails.txt

# Comparer avec le run précédent pour identifier les régressions
diff previous-fails.txt current-fails.txt
```

## Intégration avec des outils externes

RHACS peut pousser les résultats vers :
- **Splunk** (via notifier)
- **Google Cloud SCC**
- **Microsoft Sentinel**
- **Webhook** vers un SIEM custom

---

## Résumé pour l'examen

> - Rapport manuel : **Compliance → [Standard] → Generate Report** (PDF ou CSV)
> - Rapport planifié : **Compliance → Reporting → Create Schedule**
> - Format CSV : contrôle par contrôle avec statut Pass/Fail/N/A
> - Résultats bruts OpenSCAP accessibles dans le PV du Compliance Operator
> - Export API : `GET /v1/compliance/results?standard=<standard>`
> - Pousser les résultats vers SIEM via les notifiers RHACS
