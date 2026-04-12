# 3.5 — Enforce runtime policies on a secured cluster

## Lifecycle Runtime

Les policies **Runtime** sont un **superset** des autres lifecycles (DO430 p.207) :

> *"A runtime policy can include all build-time and deploy-time policy criteria. A runtime policy can also include data about process executions during runtime."*

Elles évaluent **à la fois** :
- Les critères statiques (config du déploiement, CVE des images) — hérités de Build/Deploy
- L'**activité en cours** dans les conteneurs en cours d'exécution :
  - Processus lancés (nom, path, arguments)
  - Connexions réseau établies
  - Appels système (syscalls)
  - Activité de fichiers

La détection est assurée par **Collector** (DaemonSet CORE_BPF) remontant les événements à Sensor.

## Types d'événements Runtime

| Type | Exemple de détection |
|---|---|
| **Process** | `/usr/bin/nmap` exécuté dans un conteneur web |
| **Network flow** | Connexion sortante vers une IP suspecte |
| **Syscall** | `ptrace()` appelé dans un conteneur |
| **Filesystem** | Écriture dans `/etc/passwd` |

## Modes d'enforcement Runtime

| Mode | Comportement |
|---|---|
| **Inform** | Violation créée dans l'UI, conteneur non affecté |
| **Kill pod** | Le pod est immédiatement supprimé |

> **Kill pod** est l'**unique** action d'enforcement disponible en Runtime. Le pod est supprimé et (si géré par un Deployment) recréé propre.

## Configurer l'enforcement Runtime

### Via l'UI

1. **Policy Management → [Policy Runtime] → Edit**
2. **Response Method** : `Inform and Enforce`
3. **Enforcement Actions** → `Kill Pod`

## Exemples de policies Runtime par défaut

| Policy | Détection |
|---|---|
| `Cryptocurrency Mining Process Execution` | xmrig, minerd, cpuminer… |
| `Shell Spawned by Java Application` | /bin/bash, /bin/sh depuis un process Java |
| `Network Management Execution` | iptables, nmap, tcpdump… |
| `Remote File Copy (wget/curl in pod)` | wget, curl avec téléchargement |
| `Process with UID 0 in exec` | exec en root dans un conteneur non-root |

## Tester une policy Runtime

```bash
# 1. Déployer un conteneur de test
oc run test-runtime --image=registry.access.redhat.com/ubi9:latest \
  --command -- sleep 3600 -n test

# 2. Déclencher la violation
oc exec test-runtime -n test -- nmap localhost

# 3. Vérifier dans l'UI : Violations → filter Lifecycle=Runtime
# Si policy "nmap" en Enforce → pod tué automatiquement
```

## Process baselines (lien avec Runtime)

RHACS apprend les processus légitimes d'un déploiement pendant une **période de baseline** (configurable). Les processus hors baseline peuvent déclencher une policy Runtime.

```bash
# UI : Deployments → [déploiement] → Process Discovery
# Voir les processus observés et gérer la baseline
```

## Vérifier les violations Runtime

```bash
# UI : Violations → Lifecycle=Runtime
# Chaque violation montre :
# - Processus exact (path + arguments + PID)
# - Container + pod concerné
# - Timestamp
# - Action prise (Kill pod si Enforce)
```

## Monitoring via l'API

```bash
# Lister les violations Runtime actives
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$ROX_ENDPOINT/v1/alerts?query=Lifecycle Stage:RUNTIME,Violation State:ACTIVE" | \
  jq '.alerts[] | {policy: .policy.name, deployment: .deployment.name, time: .time}'
```

## Limites du Kill pod

- Pods gérés par Deployment/StatefulSet → recréés automatiquement (sain !)
- Pods standalone → supprimés définitivement
- Si le problème persiste au redémarrage → cycle infini kill/restart (surveiller !)

---

## Résumé pour l'examen

> - Runtime = **superset** : peut inclure critères Build + Deploy + activité en cours (process, réseau, syscall)
> - Seule action d'enforcement : **Kill pod**
> - Détection basée sur les événements remontés par Collector → Sensor → Central
> - Policy Runtime + Enforce = pod supprimé dès la détection
> - Pods recréés par leur Deployment → normal, si le trigger persiste c'est un indicateur
> - Process baselines : RHACS apprend les processus légitimes pour réduire les faux positifs
