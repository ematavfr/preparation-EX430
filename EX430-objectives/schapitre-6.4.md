# 6.4 — Integrate object storage for managing backups

## Prérequis

RHACS peut sauvegarder sa base de données (PostgreSQL) vers :
- **Amazon S3** (ou compatible : MinIO, Ceph RGW, etc.)
- **Google Cloud Storage (GCS)**

La sauvegarde inclut :
- Toutes les données Central (policies, configurations, violations, CVE data)
- Les certificats et secrets

## Types d'intégrations S3 disponibles

| Type dans l'UI | Quand l'utiliser |
|---|---|
| **Amazon S3** | AWS S3 natif avec IAM ou Access Key |
| **S3 API Compatible** | ODF/Noobaa, MinIO, Ceph RGW — nécessite l'endpoint custom |

> **Point clé examen** : pour ODF/Noobaa, choisir **"S3 API Compatible"** (pas "Amazon S3") et renseigner l'endpoint `host_base`. L'option signature V2 peut être requise selon la config ODF.

## Configurer une intégration S3

### Via l'UI

1. **Platform Configuration → Integrations → Backup Integrations → Amazon S3**
2. Renseigner :

```
Name: backup-s3-prod
Bucket: rhacs-backups-prod
Region: eu-west-1
Prefix: rhacs/           (sous-dossier dans le bucket)
Access Key ID: AKIA...
Secret Access Key: ****
Use IAM: false (ou true si IRSA/IAM role)
```

3. **Test → Save**

### S3 avec credentials IAM (IRSA sur AWS)

```json
{
  "type": "s3",
  "s3": {
    "bucket": "rhacs-backups",
    "region": "eu-west-1",
    "useIam": true
  }
}
```

L'IAM role du pod Central doit avoir la policy `s3:PutObject` sur le bucket.

### Via l'API

```bash
curl -sk -X POST "$ROX_ENDPOINT/v1/externalbackups" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "backup-s3-prod",
    "type": "s3",
    "schedule": {
      "intervalType": "WEEKLY",
      "weekly": {"day": 0},
      "hour": 2,
      "minute": 0
    },
    "backupsToKeep": 7,
    "s3": {
      "bucket": "rhacs-backups-prod",
      "region": "eu-west-1",
      "accessKeyId": "AKIA...",
      "secretAccessKey": "****",
      "objectPrefix": "rhacs/"
    }
  }'
```

## Configurer une intégration GCS

```bash
curl -sk -X POST "$ROX_ENDPOINT/v1/externalbackups" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "backup-gcs-prod",
    "type": "gcs",
    "gcs": {
      "bucket": "rhacs-backups-gcs",
      "objectPrefix": "rhacs/",
      "serviceAccount": "<JSON key content>"
    }
  }'
```

## Schedule de sauvegarde

| Paramètre | Description |
|---|---|
| `intervalType` | DAILY ou WEEKLY |
| `hour` / `minute` | Heure UTC de déclenchement |
| `backupsToKeep` | Nombre de sauvegardes à conserver (rotation) |

## Déclencher une sauvegarde manuelle

```bash
# Via UI : Integrations → [backup config] → Trigger Backup Now
# Via API :
curl -sk -X POST "$ROX_ENDPOINT/v1/db/backup" \
  -H "Authorization: Bearer $TOKEN" \
  --output central-backup-$(date +%Y%m%d).zip
```

## Vérifier les sauvegardes dans le bucket

```bash
# S3
aws s3 ls s3://rhacs-backups-prod/rhacs/ --recursive

# MinIO / Ceph compatible S3
s3cmd ls s3://rhacs-backups-prod/rhacs/
```

---

## Résumé pour l'examen

> - Backup integrations : **Platform Configuration → Integrations → Backup Integrations**
> - Supports : **S3** (ou compatible) et **GCS**
> - Configurer : bucket + credentials + schedule + rétention (`backupsToKeep`)
> - Sauvegarde manuelle : UI → Trigger Backup Now, ou `POST /v1/db/backup`
> - `roxctl central backup` = alternative CLI pour déclencher le backup
> - IAM/IRSA supporté pour éviter les credentials statiques sur AWS
