# 4.5 — Manage build-time policy generation and enforcement

## Build-time lifecycle

Les policies **Build-time** sont évaluées pendant le **build de l'image** ou en **CI/CD**, avant tout déploiement. Objectif : shift-left security.

## roxctl image check

```bash
roxctl image check \
  --image=registry.io/myapp:1.0 \
  --endpoint=$ROX_ENDPOINT \
  --insecure-skip-tls-verify \
  --output=table
```

```
POLICY                    SEVERITY   BREAKING  DESCRIPTION
Fixable CVSS >= 9         CRITICAL   Yes       Image has fixable CVE with CVSS >= 9
Latest tag                MEDIUM     No        Image uses latest tag
```

**Exit codes :**
- `0` : aucune policy `Enforce` violée → pipeline continue
- `1` : policy `Enforce` violée → pipeline s'arrête

## roxctl image scan

```bash
roxctl image scan \
  --image=registry.io/myapp:1.0 \
  --endpoint=$ROX_ENDPOINT \
  --output=json
```

Retourne les CVE sans évaluation des policies (scan brut).

## Configurer une policy Build-time

```yaml
Policy:
  name: "No Critical CVE at Build"
  lifecycleStages: [BUILD]
  criteria:
    - fieldName: CVSS
      values: [{value: "9"}]
      operator: GREATER_THAN_OR_EQUALS
  enforcementActions: [FAIL_BUILD_ENFORCEMENT]
```

## Intégration CI/CD

### Tekton

```yaml
- name: rhacs-image-check
  taskRef:
    name: rhacs-image-check   # Task disponible sur Tekton Hub
  params:
    - name: IMAGE
      value: $(params.IMAGE)
    - name: ROX_API_TOKEN
      value: $(params.ROX_API_TOKEN)
    - name: ROX_CENTRAL_ENDPOINT
      value: $(params.ROX_CENTRAL_ENDPOINT)
```

### Jenkins

```groovy
stage('RHACS Security Check') {
  steps {
    sh "roxctl image check --image=${IMAGE} --endpoint=${ROX_ENDPOINT}"
  }
}
```

## roxctl netpol generate (build-time)

```bash
# Générer des NetworkPolicies depuis des manifests locaux (sans cluster)
roxctl netpol generate ./k8s-manifests/ \
  --output-dir ./netpols/

# Analyser la connectivité réseau déclarée
roxctl netpol connectivity map ./k8s-manifests/
```

## Différence des lifecycles

| Lifecycle | Quand | Qui évalue |
|---|---|---|
| **Build** | CI/CD, avant déploiement | roxctl (CLI) |
| **Deploy** | lors du kubectl apply | Admission Controller |
| **Runtime** | Pendant l'exécution | Collector |

---

## Résumé pour l'examen

> - Build-time = évaluation **avant déploiement**, en CI/CD
> - `roxctl image check` → exit code 1 si policy Enforce violée
> - `roxctl image scan` → scan brut CVE (sans évaluation policies)
> - Policy Build-time : `lifecycleStages: [BUILD]` + `FAIL_BUILD_ENFORCEMENT`
> - `roxctl netpol generate` sur manifests locaux = NetworkPolicies sans cluster
> - Intégration native Tekton (tasks sur Tekton Hub)
