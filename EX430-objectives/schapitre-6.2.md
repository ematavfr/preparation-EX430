# 6.2 — Troubleshoot common issues with integration

## Méthodologie générale

```
1. Reproduire l'erreur
2. Consulter les logs RHACS (Central, Scanner, Sensor)
3. Tester l'intégration depuis l'UI (bouton Test)
4. Vérifier la connectivité réseau
5. Vérifier les credentials
```

## Problèmes courants — Registry

### Authentification échouée

```
Error: unauthorized: access to the requested resource is not authorized

Causes possibles :
- Credentials incorrects (username/password/token expiré)
- Robot account sans permission de pull
- Token ECR expiré (TTL 12h)

Solutions :
- Régénérer le token/robot account
- Vérifier les permissions dans le registry
- Pour ECR : s'assurer que l'IAM role a ecr:GetAuthorizationToken
```

### TLS/Certificat invalide

```
Error: x509: certificate signed by unknown authority

Solutions :
- Décocher "Verify TLS" dans l'intégration (registry dev/test uniquement)
- Ajouter le CA du registry dans un Secret et le référencer dans la CR
```

### Timeout de connexion

```
Error: dial tcp x.x.x.x:443: i/o timeout

Causes :
- NetworkPolicy bloque le pod Scanner vers le registry
- Firewall bloque le port 443
- Registry interne non joignable depuis le cluster

Solutions :
- Vérifier NetworkPolicies dans le namespace stackrox
- Vérifier la connectivité : oc exec -it scanner-xxx -- curl -v https://registry-url
```

## Problèmes courants — Sensor

### Sensor ne se connecte pas à Central

```
Symptômes : cluster Unhealthy dans l'UI RHACS
Logs : oc logs -l app=sensor -n stackrox

Causes fréquentes :
- Init bundle expiré (certificats TLS périmés)
- Central inaccessible depuis le cluster sécurisé (réseau)
- Secret d'init bundle supprimé ou corrompu

Solutions :
- Générer un nouvel init bundle et l'appliquer
- Vérifier la résolution DNS de Central depuis le cluster
- oc rollout restart deployment/sensor -n stackrox
```

### Collector ne démarre pas

```
Causes :
- Node tainté sans toleration appropriée dans la CR
- Kernel module incompatible (utiliser EBPF plutôt que KERNEL_MODULE)

Solutions :
oc get ds collector -n stackrox -o yaml | grep -A5 tolerations
# Vérifier et adapter taintToleration dans SecuredCluster CR
```

## Problèmes courants — Scanner

### Scanner ne scanne pas les images

```
Causes :
- Scanner en attente (pas assez de replicas)
- Timeout scanner (image trop grosse)
- Credentials registry manquants

Solutions :
oc get pods -n stackrox | grep scanner
oc logs -l app=scanner -n stackrox
```

## Outils de diagnostic

```bash
# Santé générale de Central
roxctl central debug dump -e $ROX_ENDPOINT > debug.zip

# Logs Central
oc logs -l app=central -n stackrox --tail=100

# Logs Sensor
oc logs -l app=sensor -n stackrox --tail=100

# Logs Collector (sur un nœud spécifique)
oc logs -l app=collector -n stackrox --field-selector spec.nodeName=worker-1

# Tester la connectivité Sensor→Central
oc exec -it deployment/sensor -n stackrox -- \
  wget -qO- https://central.stackrox.svc:443/v1/ping
```

## System Health dans l'UI

**Platform Configuration → System Health**

Affiche :
- État de Central, Scanner, Sensor, Collector
- Erreurs d'intégration détectées
- Expiration des init bundles

---

## Résumé pour l'examen

> - Commencer par **Platform Configuration → System Health** pour une vue d'ensemble
> - Sensor unhealthy → vérifier init bundle (expiration) + réseau
> - Registry auth error → credentials/token + permissions pull
> - TLS error → décocher "Verify TLS" ou ajouter le CA
> - `roxctl central debug dump` pour collecter tous les diagnostics en un fichier
> - Collector ne démarre pas → vérifier tolerations + passer en EBPF
