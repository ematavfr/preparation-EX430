# 6.5 — Use s3cmd tool to consult buckets

## s3cmd — présentation

`s3cmd` est un outil CLI Python pour interagir avec des buckets S3 (Amazon S3 ou compatibles comme MinIO, Ceph RGW, Noobaa).

Dans le contexte EX430, il est utilisé pour **consulter et récupérer les sauvegardes RHACS** stockées dans un bucket S3-compatible.

## Installation

```bash
# RHEL/CentOS
dnf install s3cmd -y

# Python pip
pip install s3cmd
```

## Configuration de s3cmd

### Interactive

```bash
s3cmd --configure
# Questions posées :
# - Access Key: AKIA...
# - Secret Key: ****
# - Default Region: eu-west-1 (ou laisser vide pour MinIO)
# - S3 Endpoint: s3.amazonaws.com (ou URL MinIO: minio.company.com:9000)
# - DNS-style bucket+hostname:port: %(bucket)s.s3.amazonaws.com
# - Encryption: No (pour les tests)
# - Use HTTPS: Yes
# Config saved to: ~/.s3cfg
```

### Manuel (~/.s3cfg)

```ini
[default]
access_key = AKIA...
secret_key = ****
host_base = s3.amazonaws.com
host_bucket = %(bucket)s.s3.amazonaws.com
use_https = True
# Pour MinIO :
# host_base = minio.company.com:9000
# host_bucket = minio.company.com:9000/%(bucket)s
```

### Config pour OpenShift Data Foundation / ODF (environnement examen DO430)

```ini
[default]
access_key = <ACCESS_KEY>
secret_key = <SECRET_KEY>
host_base = s3-openshift-storage.apps.ocp4.example.com
host_bucket = s3-openshift-storage.apps.ocp4.example.com/%(bucket)s
signature_v2 = True
```

> **`signature_v2 = True`** est requis pour la compatibilité avec Noobaa/ODF.

### Récupérer les infos du bucket depuis un ConfigMap (lab DO430)

```bash
# Les credentials et infos bucket peuvent être stockés dans un ConfigMap
oc extract --to=- cm/backup-acs -n integration-backup
# Retourne : BUCKET_NAME, BUCKET_HOST, BUCKET_PORT, BUCKET_REGION

# Stocker le nom du bucket
export BUCKET_NAME=$(oc extract --to=- cm/backup-acs -n integration-backup 2>/dev/null | grep BUCKET_NAME | cut -d= -f2)
```

## Commandes essentielles

```bash
# Lister tous les buckets (avec taille et date)
s3cmd la

# Lister tous les buckets (sans détails)
s3cmd ls

# Lister le contenu d'un bucket
s3cmd ls s3://rhacs-backups-prod/

# Lister récursivement
s3cmd ls s3://rhacs-backups-prod/rhacs/ --recursive

# Afficher la taille des objets
s3cmd ls s3://rhacs-backups-prod/rhacs/ -l

# Télécharger un fichier
s3cmd get s3://rhacs-backups-prod/rhacs/backup-20260412.zip ./backup.zip

# Télécharger tout un préfixe
s3cmd sync s3://rhacs-backups-prod/rhacs/ ./local-backups/

# Uploader un fichier
s3cmd put ./backup.zip s3://rhacs-backups-prod/rhacs/

# Supprimer un fichier
s3cmd del s3://rhacs-backups-prod/rhacs/old-backup.zip

# Informations sur un objet
s3cmd info s3://rhacs-backups-prod/rhacs/backup-20260412.zip
```

## Avec un endpoint MinIO ou Ceph

```bash
# Spécifier l'endpoint à la volée
s3cmd --host=minio.company.com:9000 \
      --host-bucket=minio.company.com:9000/%(bucket)s \
      --no-ssl \
      ls s3://rhacs-backups/
```

## Cas d'usage EX430 : vérifier la présence du backup RHACS

```bash
# 1. Configurer s3cmd
s3cmd --configure

# 2. Lister les backups
s3cmd ls s3://rhacs-backups/rhacs/ -l

# 3. Télécharger le dernier backup pour vérification
s3cmd get s3://rhacs-backups/rhacs/backup-latest.zip ./

# 4. Vérifier le contenu du zip
unzip -l backup-latest.zip
```

## Différence s3cmd vs aws CLI

| Critère | s3cmd | aws CLI |
|---|---|---|
| Config | ~/.s3cfg | ~/.aws/credentials |
| MinIO compatible | Oui (host_base) | Oui (--endpoint-url) |
| Syntaxe | `s3cmd ls s3://bucket/` | `aws s3 ls s3://bucket/` |
| Installation | `dnf install s3cmd` | `pip install awscli` |

---

## Résumé pour l'examen

> - `s3cmd --configure` = configuration interactive (access key + secret + endpoint)
> - Config stockée dans `~/.s3cfg`
> - **`s3cmd la`** = list all avec taille (utilisé dans les labs DO430)
> - Commandes clés : `s3cmd ls/la`, `s3cmd get`, `s3cmd put`, `s3cmd sync`
> - Pour ODF/Noobaa : `signature_v2 = True` dans `.s3cfg` (requis)
> - Infos bucket récupérables via `oc extract --to=- cm/backup-acs`
> - Cas d'usage EX430 : consulter et télécharger les sauvegardes RHACS
