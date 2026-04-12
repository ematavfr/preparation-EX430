# 4.3 — Audit listening endpoints

## Concept

Les **listening endpoints** sont les ports sur lesquels les processus dans les conteneurs **écoutent activement**, détectés par Collector via eBPF.

Contrairement aux `containerPort` Kubernetes (déclaratifs), ce sont les ports **réellement ouverts** à l'exécution.

## Accéder aux listening endpoints

### Via Network Graph

**Network → Network Graph → [clic sur un deployment]** → onglet **Listening Endpoints**

Affiche :
- Port numéro + protocole (TCP/UDP)
- Process qui écoute (nom + PID)
- Container concerné

### Via API

```bash
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$ROX_ENDPOINT/v1/listeningendpoints/deployment/<deployment-id>" | jq .
```

## Cas d'usage : détecter des ports inattendus

```
Déploiement: webapp (namespace: production)
Ports déclarés Kubernetes: 8080/tcp

Listening endpoints détectés:
├── 8080/tcp → java (attendu)
├── 9090/tcp → java (metrics - OK si connu)
└── 4444/tcp → bash (SUSPECT ! shell listener)
```

Le port 4444 n'est pas dans le YAML → anomalie à investiguer immédiatement.

## Comparer avec les NetworkPolicies

Un port qui écoute sans NetworkPolicy correspondante = surface d'attaque ouverte.

```bash
oc get networkpolicies -n production
# Comparer avec les listening endpoints RHACS
```

## containerPort vs listening endpoint

| Critère | containerPort (YAML) | Listening endpoint (RHACS) |
|---|---|---|
| Source | Déclaration statique | Observation runtime (eBPF) |
| Fiable ? | Non (déclaratif, pas enforced) | Oui (réalité du runtime) |
| Visibilité | kubectl get pod -o yaml | RHACS Network Graph |
| Usage | Documentation, Services | Audit sécurité réel |

---

## Résumé pour l'examen

> - Listening endpoints = ports **réellement ouverts** à l'exécution (Collector eBPF)
> - Différent des `containerPort` Kubernetes qui sont déclaratifs
> - Visible dans : Network Graph → [deployment] → Listening Endpoints
> - Cas d'usage clé : détecter un **shell listener** ou service non déclaré
> - Comparer avec les NetworkPolicies pour identifier les lacunes de restriction
