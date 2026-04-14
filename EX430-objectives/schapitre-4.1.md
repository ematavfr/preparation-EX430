# 4.1 — Analyze network traffic with the network graph

## Network Graph — vue d'ensemble

Navigation : **Network → Network Graph**

Le network graph visualise les **flux réseau réels** observés par Collector (eBPF) sur les clusters sécurisés.

## Éléments du graph

| Élément | Représentation |
|---|---|
| **Namespace** | Rectangle coloré groupant les déploiements |
| **Deployment** | Nœud circulaire dans un namespace |
| **Flux actif** | Flèche pleine (trafic observé récemment) |
| **Flux de baseline** | Flèche tiretée (appris dans la baseline) |
| **External sources** | Nœud spécial pour les IPs/CIDR externes |
| **Anomalies** | Flèche rouge (flux hors baseline) |

## Filtres et navigation

- **Cluster selector** — sélectionner le cluster à visualiser
- **Namespace filter** — afficher 1 ou N namespaces
- **Deployment filter** — zoomer sur un déploiement
- **Time range** — trafic des dernières 1h / 24h / 7j
- **"Anomalous flows only"** — afficher uniquement les flux inattendus

## Analyser un déploiement spécifique

1. Cliquer sur un nœud deployment → panneau latéral
2. Informations affichées :
   - **Ingress connections** : qui se connecte à ce déploiement
   - **Egress connections** : vers où ce déploiement se connecte
   - **Ports** : ports utilisés
   - **Protocols** : TCP/UDP
   - **Baseline status** : flux dans ou hors baseline

## Types de connexions

| Type | Description |
|---|---|
| **Deployment → Deployment** | Flux intra-cluster |
| **Deployment → External** | Sortie vers internet/réseau externe |
| **External → Deployment** | Entrée depuis internet (ex: LoadBalancer) |
| **Deployment → CIDR block** | Flux vers un sous-réseau |

> RHACS détecte et met en évidence automatiquement les **blocs CIDR publics connus** (Google Cloud, AWS, Microsoft Azure) comme entités externes distinctes dans le graph.

## Identifier les anomalies réseau

```
Workflow d'investigation :
1. Network Graph → activer "Show Anomalous Flows"
2. Identifier les flèches rouges (flux hors baseline)
3. Cliquer sur le flux → voir source, destination, port, volume
4. Décider :
   - flow légitime → ajouter à la baseline
   - flow suspect  → investiguer, créer une policy d'alerte
```

## Listening Endpoints (dans le graph)

Visible dans le panneau latéral d'un deployment :
- **Listening ports** : ports sur lesquels le conteneur écoute (détecté par Collector)
- Permet d'identifier des services exposés inattendus

---

## Résumé pour l'examen

> - Network Graph = visualisation des flux **réels** observés par Collector
> - Nœuds = deployments, flèches = flux (plein=actif, tiret=baseline, rouge=anomalie)
> - Filtrer par namespace/cluster/time range
> - "Anomalous flows" = flux non présents dans la baseline → à investiguer
> - Cliquer sur un nœud → ingress/egress par port/protocole
