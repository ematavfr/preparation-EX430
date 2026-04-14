# 1.2 — Deploy the RHACS operator

## Prérequis

- OpenShift 4.11+ (ou Kubernetes 1.24+)
- Accès `cluster-admin`
- Namespace `rhacs-operator` créé automatiquement par OLM
- Architectures supportées : `amd64`, `ppc64le`, `s390x`

## Sizing minimum (source : Installing guide 4.6)

| Composant | CPU Request | CPU Limit | RAM Request | RAM Limit | Stockage |
|---|---|---|---|---|---|
| **Central** | 1.5 cores | 4 cores | 4 GiB | 8 GiB | — |
| **Central DB** | 4 cores | 8 cores | 8 GiB | 16 GiB | **100 GiB** |
| **Nœud (Secured Cluster)** | 3 cores min | — | 6 GiB min | — | — |

> **Point clé examen** : Central DB nécessite **100 GiB** de stockage persistant — c'est la cause principale de PVC Pending si le StorageClass ne peut pas provisionner ce volume.

## Installer l'opérateur ACS via OLM

```bash
# Depuis l'UI : OperatorHub → "Advanced Cluster Security for Kubernetes"
# Channel recommandé : stable (ex: stable-4.6)

# Via CLI :
cat <<EOF | oc apply -f -
apiVersion: operators.coreos.com/v1alpha1
kind: Subscription
metadata:
  name: rhacs-operator
  namespace: rhacs-operator
spec:
  channel: stable
  name: rhacs-operator
  source: redhat-operators
  sourceNamespace: openshift-marketplace
EOF
```

```bash
oc get csv -n rhacs-operator
# NAME                        PHASE
# rhacs-operator.v4.6.x       Succeeded

oc get pods -n rhacs-operator
```

## Déployer Central (cluster hub)

```bash
oc new-project stackrox
```

```yaml
apiVersion: platform.stackrox.io/v1alpha1
kind: Central
metadata:
  name: stackrox-central-services
  namespace: stackrox
spec:
  central:
    exposure:
      route:
        enabled: true          # Route OpenShift (recommandé sur OCP)
    persistence:
      persistentVolumeClaim:
        storageClassName: gp3
  egress:
    connectivityPolicy: Online  # accès internet pour flux CVE
  scanner:
    scannerComponent: Enabled
    analyzer:
      scaling:
        autoScaling: Enabled
        minReplicas: 2
        maxReplicas: 5
```

```bash
oc apply -f central.yaml
oc get central -n stackrox
oc get pods -n stackrox -w
```

### Récupérer le mot de passe admin initial

```bash
oc get secret central-htpasswd -n stackrox \
  -o jsonpath='{.data.password}' | base64 -d
```

## Générer un init bundle (prérequis SecuredCluster)

L'init bundle contient exactement **3 secrets TLS** :
- `collector-tls`
- `sensor-tls`
- `admission-control-tls`

> Le bundle **ne contient pas** de certificats Scanner — Sensor les demande dynamiquement à Central.
> Un même bundle peut être utilisé sur **plusieurs** secured clusters.

```bash
# Via UI : Platform Configuration → Clusters → Manage Tokens → Cluster Init Bundle
# Via roxctl :
roxctl -e "https://$(oc get route central -n stackrox -o jsonpath='{.spec.host}'):443" \
  central init-bundles generate mon-cluster \
  --output-secrets cluster-init-bundle.yaml

oc apply -f cluster-init-bundle.yaml -n stackrox
```

## Base de données externe (optionnel)

Central DB peut être remplacée par une PostgreSQL externe (RDS, CrunchyDB, etc.) :

```yaml
# Dans la CR Central (via Helm) :
central.db.external: true
central.db.source.connectionString: "host=mydb.example.com port=5432 dbname=central user=rhacs sslmode=require"
```

> Utilisé en production pour déléguer la HA/backup à une infra DB gérée. Non requis pour l'examen mais bon à connaître.

## Upgrade automatique des Secured Clusters

Pour les clusters installés par **manifest (roxctl)** — pas Helm/OLM :

```bash
# Activer l'upgrade automatique depuis l'UI :
# Platform Configuration → Clusters → [cluster] → Enable automatic upgrades
```

Statuts d'upgrade dans l'UI :

| Statut | Signification |
|---|---|
| `Up to date with Central` | Même version que Central |
| `Upgrade available` | Nouvelle version disponible pour Sensor/Collector |
| `Upgrade failed. Retry` | L'upgrade automatique a échoué |
| `Secured cluster version is not managed` | Helm ou Operator contrôle la version |

> **Helm et Operator** : l'upgrade automatique n'est **pas** disponible — il faut upgrader via Helm ou OLM.

## Déployer Secured Cluster Services

```yaml
apiVersion: platform.stackrox.io/v1alpha1
kind: SecuredCluster
metadata:
  name: stackrox-secured-cluster-services
  namespace: stackrox
spec:
  clusterName: mon-cluster
  centralEndpoint: central.stackrox.svc:443
  admissionControl:
    listenOnCreates: true
    listenOnUpdates: true
    listenOnEvents: true
  collector:
    collection: EBPF
    taintToleration: TolerateTaints
```

```bash
oc apply -f secured-cluster.yaml
oc get securedcluster -n stackrox
oc get pods -n stackrox
# Attendu : admission-control (x3), collector (DaemonSet), sensor (x1)
```

---

## Résumé pour l'examen

> - Opérateur : namespace `rhacs-operator`, composants dans `stackrox`
> - **Central CR** → UI + API + Scanner (hub cluster uniquement)
> - **init bundle** → 3 secrets TLS (`collector-tls`, `sensor-tls`, `admission-control-tls`) requis **avant** de créer le SecuredCluster
> - Un init bundle = utilisable sur **N** secured clusters
> - **SecuredCluster CR** → Sensor + Collector + Admission Controller sur chaque cluster surveillé
> - `connectivity: Online` = mise à jour automatique des feeds CVE
> - **Sizing Central DB** : 4 cores / 8 GiB RAM / **100 GiB** stockage (PVC Pending si StorageClass insuffisante)
> - **Nœuds Secured Cluster** : 3 cores / 6 GiB RAM minimum
> - Upgrade automatique Sensor : disponible uniquement pour installations **manifest (roxctl)** — pas Helm/OLM
