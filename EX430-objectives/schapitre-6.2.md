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

## Problèmes courants — OIDC

### redirect_uri mismatch

```
Error: redirect_uri_mismatch — the redirect URI in the request did not match

Cause : L'URL de callback déclarée dans le provider OIDC ne correspond pas
        à l'URL réelle de Central.

Solution :
- Dans le provider OIDC (Keycloak, Okta...) : ajouter exactement cette URL :
  https://<central-host>/sso/providers/oidc/callback
- Vérifier que <central-host> correspond à la Route OpenShift sans slash final
```

### client_id ou client_secret invalide

```
Error: invalid_client — client authentication failed

Solutions :
- Vérifier les credentials dans RHACS UI :
  Platform Configuration → Integrations → Authentication Providers → [provider] → Edit
- Régénérer le client secret dans le provider OIDC
- S'assurer que le client OIDC est actif (non désactivé dans Keycloak/Okta)
```

### Claims de rôle non mappés

```
Symptôme : l'utilisateur se connecte mais a des droits insuffisants (ou None)

Cause : les claim mappings RHACS ne correspondent pas aux claims retournés par le token.

Diagnostic :
- Décoder le token JWT reçu : https://jwt.io
- Comparer les claims avec les règles de mapping dans RHACS

Solution :
- Platform Configuration → Access Control → [Auth Provider] → Rules
- Ajuster les règles de mapping (ex: groups claim → role RHACS)
```

## Problèmes courants — Object Storage (S3/ODF)

### Connexion refusée ou timeout

```
Error: dial tcp x.x.x.x:443: connection refused

Causes :
- Endpoint S3 incorrect (URL, port)
- NetworkPolicy bloque Central vers l'endpoint S3
- Certificat TLS non reconnu (ODF avec cert auto-signé)

Solutions :
- Vérifier l'URL dans Platform Configuration → Integrations → Backup Integrations
- Tester depuis Central : oc exec -it deployment/central -n stackrox \
    -- curl -v https://<s3-endpoint>/
- Pour ODF/Noobaa : cocher "Disable TLS" ou fournir le CA ODF
```

### Accès refusé au bucket

```
Error: AccessDenied — Access Denied

Causes :
- Access Key / Secret Key incorrects
- Le bucket n'existe pas encore
- Politique IAM/bucket trop restrictive

Solutions :
- Vérifier les credentials : oc extract --to=- cm/backup-acs -n integration-backup
- Créer le bucket s'il n'existe pas
- S'assurer que l'utilisateur S3 a les droits : s3:PutObject, s3:GetObject, s3:ListBucket
```

### Incompatibilité signature (ODF/Noobaa)

```
Error: SignatureDoesNotMatch

Cause : ODF/Noobaa requiert Signature V2 — RHACS envoie par défaut V4.

Solution (s3cmd) :
  signature_v2 = True  # dans ~/.s3cfg

Solution (intégration RHACS) :
  Vérifier que l'endpoint est configuré comme "S3-compatible" (pas AWS natif)
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
> - **OIDC redirect_uri** : URL exacte = `https://<central-host>/sso/providers/oidc/callback`
> - **OIDC claims vides** : décoder le JWT et aligner les mapping rules dans Access Control
> - **S3 AccessDenied** : vérifier credentials + droits (PutObject, GetObject, ListBucket)
> - **S3 SignatureDoesNotMatch** sur ODF/Noobaa → `signature_v2 = True` (s3cmd) ou endpoint S3-compatible (RHACS)
