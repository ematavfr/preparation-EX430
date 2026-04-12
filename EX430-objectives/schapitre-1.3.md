# 1.3 — Configure RHACS Central and its components

## Accès à la console Central

```bash
# Obtenir l'URL
oc get route central -n stackrox -o jsonpath='{.spec.host}'

# Mot de passe admin initial
oc get secret central-htpasswd -n stackrox \
  -o jsonpath='{.data.password}' | base64 -d
```

## Configuration post-déploiement de Central

### 1. Vérifier la connexion des clusters sécurisés

UI : **Platform Configuration → Clusters**

- Statut attendu : `Healthy` (vert)
- Composants surveillés : Sensor, Collector, Admission Control

```bash
roxctl -e "https://<central>:443" central cluster list
```

### 2. Configurer les credentials de registre (pour le scanner)

UI : **Platform Configuration → Integrations → Image Integrations**

Ou via l'API :
```bash
curl -k -X POST https://<central>/v1/imageintegrations \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "quay-internal",
    "type": "quay",
    "categories": ["REGISTRY", "SCANNER"],
    "quay": {"endpoint": "quay.io", "oauthToken": "<token>"}
  }'
```

### 3. Configurer le System Health

UI : **Platform Configuration → System Health**

Surveille :
- État de Central, Scanner, Sensor, Collector
- Expiration des certificats (init bundles)
- Intégrité de la DB

### 4. Activer/configurer l'Admission Controller

```yaml
# Dans la CR SecuredCluster :
spec:
  admissionControl:
    listenOnCreates: true    # Inspecte les CREATE de workloads
    listenOnUpdates: true    # Inspecte les UPDATE de workloads
    listenOnEvents: true     # Inspecte les kubectl exec et port-forward (pas les créations)
    contactTimeout: 3        # secondes avant bypass fail-open (défaut : 3s)
```

> **Distinction clé** :
> - `listenOnCreates` / `listenOnUpdates` → contrôle des **déploiements**
> - `listenOnEvents` → contrôle des **exec** (`kubectl exec`) et **port-forward** à l'exécution

Bypass manuel (annotation à poser sur le workload) :
```yaml
metadata:
  annotations:
    admission.stackrox.io/break-glass: "true"
```

### 5. Configurer Scanner V4 (optionnel)

```yaml
# Dans la CR Central :
spec:
  scannerV4:
    scannerComponent: Enabled
    indexer:
      scaling:
        autoScaling: Enabled
    matcher:
      scaling:
        autoScaling: Enabled
```

## Configurer roxctl

```bash
# Authentification par token API
export ROX_API_TOKEN=$(oc get secret ... -o jsonpath='{.data.token}' | base64 -d)
export ROX_ENDPOINT=https://$(oc get route central -n stackrox -o jsonpath='{.spec.host}'):443

roxctl central whoami
```

### Créer un token API

UI : **Platform Configuration → Integrations → API Tokens**
- Role minimum recommandé pour CI/CD : `Continuous Integration`
- Role admin : `Admin`

## Surveillance des composants

```bash
# Logs Central
oc logs -l app=central -n stackrox -f

# Logs Sensor
oc logs -l app=sensor -n stackrox -f

# Logs Collector
oc logs -l app=collector -n stackrox -f --prefix

# État du SecuredCluster
oc get securedcluster -n stackrox -o yaml | grep -A 20 status
```

## Renouvellement des certificats (init bundle)

Les init bundles expirent (défaut : 1 an). Renouvellement :

```bash
roxctl central init-bundles generate nouveau-bundle \
  --output-secrets nouveau-bundle.yaml
oc apply -f nouveau-bundle.yaml -n stackrox
# Redémarrer le Sensor pour prendre en compte les nouveaux certs
oc rollout restart deployment/sensor -n stackrox
```

---

## Résumé pour l'examen

> - URL Central = Route OpenShift dans `stackrox`
> - Vérifier état clusters : **Platform Configuration → Clusters**
> - Admission Controller : `contactTimeout: 3s` — si Central injoignable, workload est **autorisé** (fail-open par défaut)
> - `listenOnEvents` = contrôle des `exec` et `port-forward`, **pas** des créations de pods
> - Bypass manuel : annotation `admission.stackrox.io/break-glass: "true"` sur le workload
> - Init bundles expirent → surveiller dans System Health
> - Token API nécessaire pour `roxctl` en mode non-interactif
