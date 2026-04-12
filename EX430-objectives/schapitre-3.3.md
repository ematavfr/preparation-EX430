# 3.3 — Understand the admission controller enforcement

## Rôle de l'Admission Controller

L'Admission Controller RHACS est un **webhook de validation Kubernetes** qui intercepte les requêtes à l'API server **avant** la création/modification de ressources.

```
kubectl apply / oc apply
         ↓
  kube-apiserver
         ↓
  Admission Webhook (port 443) ← RHACS Admission Controller
         ↓
  Allow / Deny (avec raison)
```

## Configuration dans SecuredCluster

```yaml
spec:
  admissionControl:
    listenOnCreates: true    # Inspecter les CREATE de workloads (pods, deployments...)
    listenOnUpdates: true    # Inspecter les UPDATE
    listenOnEvents: true     # Inspecter exec, port-forward (runtime)
    contactTimeout: 3        # Timeout en secondes avant fail-open
    bypass: BreakGlassAnnotation  # Mécanisme de bypass d'urgence
```

## Comportement en cas de timeout (fail-open)

Si Central/Sensor est **injoignable** dans le délai `contactTimeout` (défaut : 3s) :
- Le workload est **autorisé** (fail-open)
- Une violation `Attempted` est créée pour audit

> **Point clé examen** : RHACS est fail-open par défaut — la disponibilité des workloads prime sur le blocage.

## Types de ressources inspectées

| Opération | Interceptée si |
|---|---|
| `CREATE` Pod/Deployment/DaemonSet/StatefulSet/Job | `listenOnCreates: true` |
| `UPDATE` des mêmes ressources | `listenOnUpdates: true` |
| `exec` dans un conteneur | `listenOnEvents: true` |
| `port-forward` | `listenOnEvents: true` |

## Enforcement par l'Admission Controller

Une policy doit être en mode **Enforce** (et lifecycle stage `Deploy`) pour que l'AC bloque :

```yaml
Policy:
  lifecycleStages: [DEPLOY]
  enforcementActions: [FAIL_DEPLOYMENT_CREATE_ENFORCEMENT]
```

Résultat lors d'un `kubectl apply` :
```
Error from server: admission webhook "stackrox.io" denied the request:
The following policy violations were detected:
- Privileged Container: Container "main" is running with privileged mode
```

## Bypass d'urgence (break glass)

```yaml
# Annotation sur le déploiement pour bypasser le webhook :
metadata:
  annotations:
    admission.stackrox.io/bypass-policy-check: "true"
```

> Nécessite que `bypass: BreakGlassAnnotation` soit configuré dans SecuredCluster.
> Cette annotation doit être **contrôlée via RBAC** (seuls les admins peuvent l'ajouter).

## Inspecter le webhook Kubernetes

```bash
# Vérifier que le webhook est enregistré
oc get validatingwebhookconfigurations | grep stackrox

# Détail du webhook
oc get validatingwebhookconfiguration stackrox -o yaml
```

## Vérifier le fonctionnement

```bash
# Test : tenter de déployer un conteneur privileged
cat <<EOF | oc apply -f - -n test
apiVersion: v1
kind: Pod
metadata:
  name: test-priv
spec:
  containers:
  - name: main
    image: registry.access.redhat.com/ubi9:latest
    securityContext:
      privileged: true
EOF
# Attendu : erreur du webhook si policy "Privileged Container" est en Enforce
```

---

## Résumé pour l'examen

> - Admission Controller = validating webhook Kubernetes sur le cluster sécurisé
> - Intercepte : CREATE/UPDATE workloads + exec/port-forward
> - **Fail-open** : si timeout (3s), le workload passe et une violation `Attempted` est créée
> - Enforcement nécessite policy en mode `Enforce` + lifecycle `Deploy`
> - Bypass : annotation `admission.stackrox.io/bypass-policy-check: "true"` (contrôlé par RBAC)
> - Vérifier l'enregistrement : `oc get validatingwebhookconfigurations | grep stackrox`
