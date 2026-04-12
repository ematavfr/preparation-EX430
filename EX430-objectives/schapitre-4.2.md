# 4.2 — Manage network baselines

## Concept de baseline réseau

Une **network baseline** est l'ensemble des flux réseau jugés **normaux** pour un déploiement, appris automatiquement pendant une période d'observation.

Tout flux **hors baseline** = **anomalie réseau** → visible dans le graph **mais ne déclenche pas de violation automatiquement**.

> **Point clé examen** : Les anomalies sont visibles (flèche rouge) mais n'alertent pas par défaut. Il faut activer explicitement **"Enable alerts on baseline violations"** par déploiement.

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

### Activer les alertes sur anomalies

```
UI : Network Graph → [clic sur un deployment] → Flows tab
     → "Enable alerts on baseline violations" (toggle)
```

Active la génération de **violations** pour tout flux hors baseline sur ce déploiement.

### Verrouiller une baseline (Lock)

```
UI : Network Baselines → [déploiement] → Lock baseline
```

Après verrouillage :
- La baseline ne s'enrichit plus automatiquement
- Tout nouveau flux = **anomalie** (et violation si alertes activées)

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
> - Flux hors baseline = **anomalie** → visible en rouge, mais **pas de violation par défaut**
> - Activer les violations : **"Enable alerts on baseline violations"** (par déploiement)
> - **Lock baseline** → la baseline ne s'enrichit plus ; les anomalies deviennent violations si alertes activées
> - Période d'apprentissage configurable dans System Configuration
