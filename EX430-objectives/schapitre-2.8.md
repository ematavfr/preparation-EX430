# 2.8 — Assess risk in deployments

## Risk Score RHACS

RHACS calcule un **risk score** pour chaque déploiement, visible dans **Risk** (menu principal). Score de 1 à 1000+ (plus élevé = plus risqué).

Le score est une **combinaison pondérée** de plusieurs facteurs.

## Facteurs de risque

### 1. Vulnérabilités (image CVE)

| Facteur | Impact |
|---|---|
| Nombre de CVE critiques | Très élevé |
| CVE fixables | Élevé |
| CVSS score moyen | Élevé |
| CVE dans des composants exposés réseau | Élevé |

### 2. Configuration du déploiement (policy violations)

| Facteur | Impact |
|---|---|
| Container running as root | Élevé |
| Privileged container | Très élevé |
| hostPath volumes montés | Élevé |
| Capabilities dangereuses (NET_ADMIN, SYS_ADMIN) | Élevé |
| Absence de resource limits | Modéré |
| Pas de readiness/liveness probe | Faible |

### 3. Exposition réseau

| Facteur | Impact |
|---|---|
| Port exposé sur internet (LoadBalancer/NodePort) | Très élevé |
| Connections entrantes depuis internet | Élevé |
| Nombreuses connexions inter-namespaces | Modéré |

### 4. Activité runtime

| Facteur | Impact |
|---|---|
| Processus inhabituels détectés (Collector) | Élevé |
| Connexions réseau inattendues | Élevé |
| Activité syscall anormale | Modéré |

### 5. Contexte du déploiement

| Facteur | Impact |
|---|---|
| Namespace `default` ou sans politique réseau | Modéré |
| Image avec tag `latest` ou sans digest | Modéré |
| Image ancienne (pas de scan récent) | Faible |
| Replicas élevé (surface d'attaque) | Faible |

## Vue Risk dans l'UI

**Risk** → liste des déploiements triés par risk score décroissant :

- **Colonne Risk Score** : valeur numérique + barre colorée
- **Colonne Risk Factors** : facteurs contributeurs cliquables
- **Filtres** : namespace, cluster, sévérité

### Détail d'un déploiement

Cliquer sur un déploiement → panneau latéral avec :
- **Risk Indicators** : liste des facteurs avec score individuel
- **Images** : CVE et scores d'images utilisées
- **Deployment Config** : configuration Kubernetes analysée
- **Network** : connexions observées

## Priorisation avec le risk score

```
Risk score > 700  → Investigation immédiate
Risk score 400-700 → Révision dans la semaine
Risk score < 400  → Surveillance normale
```

## Policy violations impactant le risk

Les violations de policies dans le lifecycle `Deploy` contribuent directement au risk score. Corriger une violation → risk score réduit automatiquement.

```bash
# Lister les déploiements à risque via API
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$ROX_ENDPOINT/v1/deployments?query=Risk Score:>700&sort_by=risk_score" | jq .
```

---

## Résumé pour l'examen

> - Risk score : 1 à 1000+, calculé automatiquement, visible dans **Risk**
> - 5 familles de facteurs : CVE, config déploiement, exposition réseau, runtime, contexte
> - Facteur le plus impactant : **CVE critiques + container privileged + exposition internet**
> - Corriger une policy violation → risk score baisse automatiquement
> - Trier par risk score décroissant pour prioriser les investigations
