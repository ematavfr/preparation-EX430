# 5.1 — Deploy the Compliance Operator on a secured cluster

## Compliance Operator

Le **Compliance Operator** est un opérateur OpenShift qui exécute des scans de conformité sur le cluster (nodes + platform) en utilisant **OpenSCAP** comme moteur sous-jacent.

RHACS s'intègre avec le Compliance Operator pour afficher les résultats dans sa console.

## Installer le Compliance Operator

### Via OperatorHub

```bash
# UI : OperatorHub → "Compliance Operator"
# Namespace : openshift-compliance

# Via CLI :
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: compliance-operator
  namespace: openshift-compliance
spec:
  channel: stable
  name: compliance-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

```bash
oc get csv -n openshift-compliance
oc get pods -n openshift-compliance
```

## Profils disponibles

```bash
oc get profiles.compliance -n openshift-compliance
```

Profils courants :

| Profil | Standard |
|---|---|
| `ocp4-cis` | CIS Kubernetes Benchmark |
| `ocp4-cis-node` | CIS pour les nœuds |
| `ocp4-moderate` | NIST 800-53 Moderate |
| `ocp4-high` | NIST 800-53 High |
| `ocp4-pci-dss` | PCI-DSS |
| `ocp4-hipaa` | HIPAA |
| `rhcos4-cis` | CIS RHCOS (nœuds) |

## ScanSetting — configuration des scans

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSetting
metadata:
  name: default
  namespace: openshift-compliance
spec:
  rawResultStorage:
    pvAccessModes:
    - ReadWriteOnce
    storageClassName: gp3
    size: 1Gi
  roles:
  - worker
  - master
  scanTolerations:
  - operator: Exists
  schedule: "0 1 * * *"   # Cron : tous les jours à 1h
```

## ScanSettingBinding — lier profils à une configuration

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSettingBinding
metadata:
  name: cis-compliance
  namespace: openshift-compliance
spec:
  profiles:
  - apiGroup: compliance.openshift.io/v1alpha1
    kind: Profile
    name: ocp4-cis
  - apiGroup: compliance.openshift.io/v1alpha1
    kind: Profile
    name: ocp4-cis-node
  settingsRef:
    apiGroup: compliance.openshift.io/v1alpha1
    kind: ScanSetting
    name: default
```

```bash
oc apply -f scansettingbinding.yaml
```

## Alternative : planifier les scans depuis RHACS UI

> **Point clé examen** : Si vous créez un **scan schedule depuis l'UI RHACS** (Compliance → Reporting → Create Schedule), vous n'avez **pas besoin** de créer le `ScanSettingBinding` sur le Compliance Operator — RHACS le gère automatiquement.

Les deux approches sont valides :
- **Compliance Operator direct** : ScanSetting + ScanSettingBinding (contrôle granulaire)
- **RHACS UI schedule** : simplifié, sans ScanSettingBinding manuel

## Déclencher un scan manuel

```bash
# Annoter le ComplianceScan pour le re-déclencher
oc -n openshift-compliance annotate compliancescans/<scan-name> \
  compliance.openshift.io/rescan=true
```

## Vérifier les résultats

```bash
# Statut du scan
oc get compliancescans -n openshift-compliance
oc get compliancesuite -n openshift-compliance

# Résultats détaillés
oc get compliancecheckresults -n openshift-compliance | head -20

# Résultats FAIL uniquement
oc get compliancecheckresults -n openshift-compliance \
  -l compliance.openshift.io/check-status=FAIL
```

---

## Résumé pour l'examen

> - Compliance Operator → namespace `openshift-compliance`, moteur OpenSCAP
> - **ScanSetting** = configuration du scan (schedule, storage, roles)
> - **ScanSettingBinding** = association profils + ScanSetting
> - Profils clés : `ocp4-cis`, `ocp4-moderate`, `ocp4-pci-dss`, `ocp4-hipaa`
> - Re-scan manuel : annotation `compliance.openshift.io/rescan=true`
> - RHACS intègre les résultats dans sa vue Compliance
