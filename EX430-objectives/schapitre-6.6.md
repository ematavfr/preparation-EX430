# 6.6 — Backup and restore custom deployment

## Architecture de sauvegarde RHACS

```
Central (PostgreSQL) → Backup ZIP → Object Storage (S3/GCS)
                              ↕
                       roxctl central backup
```

La sauvegarde inclut :
- Base de données PostgreSQL (policies, violations, configurations)
- Certificats et secrets TLS
- Données de vulnérabilités

## Déclencher une sauvegarde

### Via roxctl

```bash
# Sauvegarde immédiate vers un fichier local
roxctl central backup \
  -e $ROX_ENDPOINT \
  --output ./backup-$(date +%Y%m%d-%H%M).zip
```

### Via l'UI

**Platform Configuration → Integrations → Backup Integrations → [config] → Trigger Backup Now**

### Via l'API

```bash
curl -sk -X POST "$ROX_ENDPOINT/v1/db/backup" \
  -H "Authorization: Bearer $TOKEN" \
  --output central-backup.zip
```

## Vérifier une sauvegarde

```bash
# Inspecter le contenu du ZIP
unzip -l central-backup.zip

# Contenu attendu :
# backup.db            ← dump PostgreSQL
# keys/                ← clés de chiffrement
# certificates/        ← certificats TLS
```

## Procédure de restauration

### Prérequis

- Central **arrêté** ou en mode maintenance
- Même version de RHACS (ou version compatible)
- Accès au fichier ZIP de sauvegarde

### Étapes de restauration

#### 1. Arrêter Central

```bash
oc scale deployment central -n stackrox --replicas=0
```

#### 2. Restaurer via roxctl

```bash
roxctl central restore \
  -e $ROX_ENDPOINT \
  ./central-backup.zip
```

#### 3. Ou restauration manuelle (via le pod de restauration)

```bash
# Créer un job de restauration RHACS
oc create job restore-central \
  --image=registry.redhat.io/advanced-cluster-security/rhacs-central-db-rhel8:4.6 \
  -n stackrox \
  -- /stackrox/bin/restore --backup-file /backup/backup.zip
```

#### 4. Redémarrer Central

```bash
oc scale deployment central -n stackrox --replicas=1
oc rollout status deployment/central -n stackrox
```

#### 5. Vérifier la restauration

```bash
# Vérifier que Central est accessible
curl -sk https://$(oc get route central -n stackrox -o jsonpath='{.spec.host}')/v1/ping

# Vérifier les données dans l'UI
# - Policies présentes
# - Violations historiques présentes
# - Clusters sécurisés (Sensor peut nécessiter un restart)
```

## Restauration des Secured Clusters après restauration Central

Après une restauration de Central, les Sensors existants peuvent perdre leur connexion (si les certificats ont changé) :

```bash
# Re-générer les init bundles
roxctl central init-bundles generate post-restore-bundle \
  --output-secrets new-bundle.yaml

oc apply -f new-bundle.yaml -n stackrox
oc rollout restart deployment/sensor -n stackrox
```

## Backup des Secured Clusters

Les Secured Clusters **n'ont pas de données persistantes à sauvegarder** — toutes les données sont dans Central. La restauration d'un Secured Cluster = re-déploiement de la CR SecuredCluster.

## Planning de sauvegarde recommandé

```
Fréquence minimum : journalière
Rétention : 7 jours minimum (backupsToKeep: 7)
Test de restauration : mensuel en environnement de test
```

---

## Résumé pour l'examen

> - `roxctl central backup` = sauvegarde directe vers fichier local
> - Sauvegarde inclut : DB PostgreSQL + certificats + clés
> - Restauration : `roxctl central restore <backup.zip>` (Central doit être arrêté)
> - Après restauration : re-générer les init bundles + restart Sensor
> - Les Secured Clusters n'ont **pas** de données persistantes à sauvegarder
> - Planifier des **tests de restauration réguliers** (point clé en prod)
