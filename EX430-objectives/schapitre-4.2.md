# 4.2 — Manage network baselines

## Concept de baseline réseau

Une **network baseline** est l'ensemble des flux réseau jugés **normaux** pour un déploiement, appris automatiquement pendant une période d'observation.

Tout flux **hors baseline** = **anomalie réseau** → peut déclencher une alerte.

## Période d'apprentissage

- Durée par défaut : **10 jours** (configurable)
- Pendant cette période : tous les flux observés sont intégrés à la baseline
- Après la période : nouveaux flux = anomalies

```bash
# UI : Platform Configuration → System Configuration
# → Network baseline observation period
```

## Accéder aux baselines

**Network → Network Graph → [clic sur un deployment] → Baseline**

Ou : **Network → Network Baselines** (liste globale)

## Gérer les entrées de baseline

### Ajouter un flux à la baseline

```
UI : Network Graph → flux anomalous → "Add to baseline"
Ou : Network Baselines → [déploiement] → [flux] → Mark as baseline
```

### Supprimer un flux de la baseline

```
UI : Network Baselines → [déploiement] → [flux] → Remove from baseline
```

### Verrouiller une baseline (Lock)

```
UI : Network Baselines → [déploiement] → Lock baseline
```

Après verrouillage :
- Tout nouveau flux = violation de policy réseau
- La baseline ne s'enrichit plus automatiquement

## États des flux

| État | Signification |
|---|---|
| `In baseline` | Flux considéré comme normal |
| `Anomalous` | Flux hors baseline (nouvelle connexion) |
| `Pending add` | En cours d'intégration à la baseline |

## API

```bash
# Lire une baseline
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$ROX_ENDPOINT/v1/networkbaselines/<deployment-id>" | jq .

# Verrouiller
curl -sk -X PATCH "$ROX_ENDPOINT/v1/networkbaselines/<deployment-id>/lock" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Résumé pour l'examen

> - Baseline = flux réseau "normaux" appris automatiquement (~10 jours)
> - Flux hors baseline = **anomalie** → visible en rouge dans le Network Graph
> - Gérer : ajouter, supprimer, ou **verrouiller** la baseline
> - **Lock baseline** → tout nouveau flux devient une violation de policy
> - Période d'apprentissage configurable dans System Configuration
