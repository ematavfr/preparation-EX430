# 3.4 — Enforce deploy-time policies on a secured cluster

## Lifecycle Deploy

Les policies **Deploy-time** sont évaluées au moment de la **création ou modification** d'un workload. Elles analysent la **configuration statique** du déploiement (pas le runtime).

Champs évalués :
- Configuration du pod/container (privileged, root, capabilities)
- Images et tags utilisés
- Montages de volumes
- Variables d'environnement
- CVE dans les images
- Labels/annotations

## Modes d'enforcement

| Mode | Comportement |
|---|---|
| **Inform** | Crée une violation visible dans l'UI, n'empêche pas le déploiement |
| **Enforce** (scale-to-zero) | Si déploiement existant viole la policy → scale replicas à 0 |
| **Enforce** (block creation) | Bloque la création via le webhook admission controller |

## Configurer le mode Enforce sur une policy

### Via l'UI

1. **Platform Configuration → Policy Management → [Policy] → Edit**
2. Onglet **Policy Behavior** → **Response Method**
3. Sélectionner : `Inform and Enforce`
4. **Enforcement Actions** → cocher `Scale to Zero Replicas` ou `Block Create/Update`

### Via l'API

```bash
curl -sk -X PUT "$ROX_ENDPOINT/v1/policies/<id>" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    ...
    "enforcementActions": ["SCALE_TO_ZERO_ENFORCEMENT"],
    "lifecycleStages": ["DEPLOY"]
  }'
```

## Actions d'enforcement disponibles (Deploy)

| Action | Description |
|---|---|
| `SCALE_TO_ZERO_ENFORCEMENT` | Scale le Deployment/ReplicaSet à 0 replicas |
| `UNSATISFIED_NODE_CONSTRAINT_ENFORCEMENT` | Ajoute un node selector impossible (pod reste Pending) |
| `FAIL_DEPLOYMENT_CREATE_ENFORCEMENT` | Bloque via Admission Controller |
| `FAIL_DEPLOYMENT_UPDATE_ENFORCEMENT` | Bloque les mises à jour via AC |

## Tester l'enforcement

```bash
# Créer un déploiement qui viole une policy en Enforce
oc create deployment test-root --image=registry.io/myapp:latest -n test
# → Si "Container Running as Root" est en Enforce : scale to zero automatique

# Vérifier
oc get deployment test-root -n test
# NAME         READY   UP-TO-DATE   AVAILABLE
# test-root    0/0     0            0   ← scalé à 0
```

## Exemple de policy Deploy-time : interdire latest tag

```yaml
# Cloner "Latest tag" policy et passer en Enforce
Policy:
  name: "No latest tag - Enforce"
  lifecycleStages: [DEPLOY]
  criteria:
    - fieldName: IMAGE_TAG
      values: [{value: "latest"}]
  enforcementActions: [SCALE_TO_ZERO_ENFORCEMENT]
  scope:
    - cluster: ocp-prod
      namespace: "production"
```

## Scope et exclusions

```yaml
# Restreindre l'enforcement à un environnement spécifique
policyScope:
  - cluster: "ocp-prod"
    namespace: "production"

# Exclure un namespace système
exclusions:
  - name: "Exclude openshift-* namespaces"
    deployment:
      scope:
        namespace: "openshift-.*"
```

## Vérification en CI/CD — roxctl deployment check

> **Point clé examen** (DO430 p.255) :
> - `roxctl image check` → vérifie contre les policies **Build-time**
> - `roxctl deployment check` → vérifie contre les policies **Deploy-time**

```bash
# Vérifier un manifest de déploiement contre les policies Deploy-time
roxctl deployment check \
  --file httpd-deployment.yaml \
  -e $ROX_ENDPOINT

# Si l'image du manifest est dans un registry connu, Central la scanne également
```

## Vérifier les violations Deploy-time

```bash
# UI : Violations → filter Lifecycle=Deploy
# Voir les violations Active (condition toujours vraie) et Attempted (bloquées)
```

---

## Résumé pour l'examen

> - Deploy-time = évaluation à la **création/modification** du workload (config statique)
> - 2 modes : **Inform** (visibilité) ou **Enforce** (blocage ou scale-to-zero)
> - `SCALE_TO_ZERO_ENFORCEMENT` : agit sur les déploiements existants
> - `FAIL_DEPLOYMENT_CREATE_ENFORCEMENT` : bloque via Admission Controller webhook
> - CI/CD : `roxctl image check` → Build-time | `roxctl deployment check` → Deploy-time
> - Toujours définir un **scope** (cluster/namespace) pour les policies Enforce
> - Exclure les namespaces système (`openshift-.*`, `kube-system`) pour éviter les faux positifs
