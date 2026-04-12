# 5.3 — Manipulate compliance reports

## Deux types de rapports (DO430)

| Type | Format | Contenu | Commande UI |
|---|---|---|---|
| **Executive report** | PDF | Score global, graphiques Pass/Fail/N/A | `Download Page as PDF` |
| **Evidence report** | CSV | Détail technique par check | `Download Evidence as CSV` |

> L'option **Export** est disponible sur **toutes** les pages Compliance et vues filtrées.

## Générer un rapport

### Via l'UI — Compliance Dashboard

1. **Compliance → Dashboard → Export** (onglet en haut à droite)
2. Sélectionner :
   - `Download Page as PDF` → rapport exécutif
   - `Download Evidence as CSV` → rapport technique détaillé

### Rapport à télécharger (file de jobs)

1. **Compliance → Dashboard → Export → Generate download**
2. Aller dans l'onglet **All report jobs**
3. Attendre que le statut passe à **Ready for download**
4. Cliquer **Ready for download** pour télécharger

> Le téléchargement est **asynchrone** — il peut prendre quelques minutes selon le volume de données.

### Rapport planifié

1. **Compliance → Reporting → Create Schedule**
2. Configurer :
   - Fréquence : Daily / Weekly / Monthly
   - Standards inclus
   - Destinataires (via notifier email)

## Format CSV — Evidence report

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

> - **Executive report** (PDF) = `Download Page as PDF` depuis **Compliance → Dashboard → Export**
> - **Evidence report** (CSV) = `Download Evidence as CSV` — détail technique par check
> - Téléchargement **asynchrone** : Generate download → All report jobs → Ready for download
> - Rapport planifié : **Compliance → Reporting → Create Schedule**
> - Résultats bruts OpenSCAP accessibles dans le PV du Compliance Operator
> - Export API : `GET /v1/compliance/results?standard=<standard>`
> - Pousser les résultats vers SIEM via les notifiers RHACS
