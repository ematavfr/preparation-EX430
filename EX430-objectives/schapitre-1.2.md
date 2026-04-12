# 1.2 — Deploy the RHACS operator

## Prérequis

- OpenShift 4.11+ (ou Kubernetes 1.24+)
- Accès `cluster-admin`
- Namespace `rhacs-operator` créé automatiquement par OLM

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

```bash
# Via UI : Platform Configuration → Clusters → Create bundle
# Via roxctl :
roxctl -e "https://$(oc get route central -n stackrox -o jsonpath='{.spec.host}'):443" \
  central init-bundles generate mon-cluster \
  --output-secrets cluster-init-bundle.yaml

oc apply -f cluster-init-bundle.yaml -n stackrox
```

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
> - **init bundle** → secrets TLS requis **avant** de créer le SecuredCluster
> - **SecuredCluster CR** → Sensor + Collector + Admission Controller sur chaque cluster surveillé
> - `connectivity: Online` = mise à jour automatique des feeds CVE
