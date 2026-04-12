# 3.2 — Examine policy violations

## Vue des violations

Navigation : **Violations** (menu principal)

### Filtres disponibles

| Filtre | Valeurs |
|---|---|
| **Lifecycle stage** | Deploy, Runtime |
| **Severity** | Critical, High, Medium, Low |
| **State** | Active, Attempted, Resolved |
| **Cluster / Namespace** | Sélection directe |
| **Policy name** | Recherche textuelle |
| **Time** | Dernière heure, 24h, 7j, custom |

## Anatomie d'une violation

```
Violation:
  Policy: "Fixable CVSS >= 9"
  Severity: Critical
  Lifecycle: Deploy
  State: Active
  Deployment: myapp (namespace: production, cluster: ocp-prod)
  Time: 2026-04-12 10:23:45
  
  Violation details:
    - Image registry.io/myapp:1.0 has component runc 1.1.6
      with CVE-2024-21626 (CVSS 8.6, Fixable in 1.1.12)
```

## États d'une violation

| État | Signification |
|---|---|
| **Active** | Violation en cours, condition toujours vraie |
| **Attempted** | Tentative bloquée par l'Admission Controller |
| **Resolved** | Condition n'est plus vraie (ex: image mise à jour) |

## Résoudre une violation manuellement

1. **Violations → [violation] → Mark as resolved**
2. Motif requis : `False positive`, `Used in test environment`, etc.

> Une violation se résout **automatiquement** si la condition n'est plus vraie (ex: le déploiement est supprimé ou l'image est mise à jour).

## Tags et commentaires

```bash
# Ajouter un commentaire sur une violation (traçabilité)
# Via UI : violation → Add comment

# Via API :
curl -sk -X POST "$ROX_ENDPOINT/v1/alerts/<id>/comments" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"message": "Investigué le 12/04 - faux positif confirmé"}'
```

## Violations Runtime

Les violations runtime incluent le **process path** exact :

```
Runtime violation:
  Policy: "Cryptocurrency Mining Process Execution"
  Container: myapp
  Process: /usr/bin/xmrig --config=/tmp/config.json
  PID: 4821
  Time: 2026-04-12 10:30:00
  
  Enforcement: Kill pod ← si policy en mode Enforce
```

## Violations Attempted (Admission Controller)

```
Attempted violation:
  Policy: "Privileged Container"
  Lifecycle: Deploy
  State: Attempted   ← workload bloqué par le webhook
  Deployment: test-privileged (namespace: default)
  Reason: Container "main" is privileged
```

## Configurer les alertes sur violations

Via les **notifiers** associés à la policy (cf. 3.1). Chaque violation déclenche une notification si un notifier est configuré.

## Violation lifecycle complet

```
Deploy → Admission Controller vérifie → Violation créée (Attempted ou Active)
                                          ↓
                                    Notifier alerté
                                          ↓
                                    Analyste investigue
                                          ↓
                              Résolu (auto ou manuel)
```

---

## Résumé pour l'examen

> - Violations visibles dans **Violations** (menu principal)
> - États : **Active** (en cours), **Attempted** (bloqué par AC), **Resolved**
> - Runtime violations : incluent le processus exact (path + args + PID)
> - Résolution automatique si la condition n'est plus vraie
> - Toujours commenter une violation résolue manuellement (traçabilité)
> - Filtres importants : lifecycle stage + severity + state + namespace
