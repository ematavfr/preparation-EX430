# 1.1 — Investigate the architecture of RHACS and its components

## Architecture globale

RHACS (basé sur StackRox) suit un modèle **hub-and-spoke** :

- **Central** : plan de contrôle, déployé **une seule fois** sur un cluster (le hub)
- **Secured Cluster Services** : plan de données, déployé sur **chaque cluster surveillé**

La communication est **unidirectionnelle** : Sensor initie la connexion vers Central (TCP 443 / gRPC over TLS). Central ne contacte jamais directement les clusters.

## Composants de Central

| Composant | Rôle |
|---|---|
| **Central** | Portal web, API REST/gRPC, moteur de policies, stockage PostgreSQL intégré |
| **Scanner V2** (StackRox Scanner) | Analyse CVE des images de conteneurs (défaut) |
| **Scanner V4** | Scanner nouvelle génération (Claircore), déployable en complément ou remplacement |
| **Scanner V4 Indexer** | Indexation des images (nœud Scanner V4) |
| **Scanner V4 Matcher** | Correspondance CVE (nœud Scanner V4) |

## Composants des Secured Cluster Services

### Obligatoires (tout cluster sécurisé)

| Composant | Déploiement | Rôle |
|---|---|---|
| **Sensor** | Deployment (1 pod) | Cerveau local. Reçoit policies de Central, les distribue à Admission Controller et Collector. Seul composant qui parle à Central (TCP 443). |
| **Admission Controller** | Deployment (3 pods HA) | Webhook Kubernetes. Inspecte create/update de workloads. Peut bloquer si violation de policy. |
| **Collector** | DaemonSet (1 pod/nœud) | Collecte trafic réseau + événements processus via eBPF ou kernel module. Remonte à Sensor. |

### Optionnels

| Composant | Quand l'activer |
|---|---|
| **Scanner V2** (local) | Scan d'images sur le cluster sécurisé sans passer par Central |
| **Scanner V4** (local) | Idem, version nouvelle génération |

## Flux de communication

```
Registry ──► Central (Scanner)
                │
         gRPC/TLS 443
                │
             Sensor ◄─── Collector (eBPF events)
                │
        Admission Controller (webhooks)
```

## roxctl CLI

Outil CLI officiel RHACS. Usages principaux :
- `roxctl central generate` — génère les manifests de déploiement
- `roxctl image scan` / `roxctl image check` — scan d'image en CI/CD
- `roxctl netpol generate` — génère des NetworkPolicies depuis le trafic observé
- `roxctl central backup` — déclenche une sauvegarde

## Ports à retenir

| Port | Usage |
|---|---|
| 443 (HTTPS/gRPC) | UI Central, API, connexion Sensor→Central |
| 8080 | Scanner V2 (interne) |
| 9090 | Collector→Sensor (gRPC, interne) |

---

## Résumé pour l'examen

> - **Central** = 1 seule instance, sur le hub cluster
> - **Secured Cluster** = Sensor + Admission Controller (3 pods) + Collector (DaemonSet)
> - Sensor est le **seul** point de contact vers Central
> - Collector utilise **eBPF** pour capturer réseau et processus
> - Scanner V2 = défaut ; Scanner V4 = nouvelle génération (Claircore)
