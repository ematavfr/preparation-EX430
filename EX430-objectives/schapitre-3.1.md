# 3.1 — Manage default security policies

## Vue d'ensemble des policies

RHACS est livré avec **+100 policies par défaut** couvrant les meilleures pratiques de sécurité Kubernetes. Elles sont organisées par :

- **Lifecycle stage** : Build, Deploy, Runtime
- **Category** : Vulnerability Management, DevOps Best Practices, Security Best Practices, Privileges, Network Tools, etc.

Navigation : **Platform Configuration → Policy Management**

## Structure d'une policy

```yaml
Policy:
  name: "Fixable CVSS >= 9"
  description: "Alert on deployments with fixable CVE with CVSS >= 9"
  severity: CRITICAL_SEVERITY
  categories: [Vulnerability Management]
  lifecycleStages: [DEPLOY]
  policyFields:             # Critères de détection
    - fieldName: CVSS
      values: [{value: "9"}]
      operator: GREATER_THAN_OR_EQUALS
    - fieldName: FIXABLE
      values: [{value: "true"}]
  enforcementActions: []    # INFORM only par défaut
  notifiers: []
  scope: []                 # Vide = tous les clusters/namespaces
```

## Actions sur les policies par défaut

| Action | Effet |
|---|---|
| **Enable/Disable** | Activer ou désactiver sans supprimer |
| **Edit** | Modifier critères, scope, enforcement |
| **Clone** | Dupliquer pour créer une variante |
| **Export** | JSON pour backup ou partage |
| **Delete** | Supprimer (impossible sur policies système) |

> Les policies marquées `System policy` ne peuvent pas être supprimées, seulement désactivées ou clonées.

## Activer/désactiver une policy

```bash
# Via UI : toggle Enable/Disable sur la policy
# Via API :
curl -sk -X PATCH "$ROX_ENDPOINT/v1/policies/<id>" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"disabled": false}'
```

## Modifier le scope d'une policy

```yaml
# Restreindre à un namespace de production :
policyScope:
  - cluster: "ocp-prod"
    namespace: "production"

# Exclure un namespace :
exclusions:
  - name: "Exclude monitoring namespace"
    deployment:
      scope:
        namespace: "monitoring"
```

## Catégories importantes pour l'examen

| Category | Exemples de policies |
|---|---|
| **Vulnerability Management** | Fixable CVSS >= 9, Container using components with known vulnerabilities |
| **Security Best Practices** | Container running as root, Privileged container, No resource limits |
| **DevOps Best Practices** | Latest tag, No liveness probe, Kubernetes dashboard deployed |
| **Network Tools** | nmap, netcat, curl in container at runtime |
| **Privileges** | Net admin capability, hostPath volume, hostPID/hostNetwork |

## Import/Export de policies

```bash
# Export d'une policy
curl -sk -H "Authorization: Bearer $TOKEN" \
  "$ROX_ENDPOINT/v1/policies/export" \
  -d '{"policyIds": ["<id>"]}' > policy-export.json

# Import
curl -sk -X POST "$ROX_ENDPOINT/v1/policies/import" \
  -H "Authorization: Bearer $TOKEN" \
  -d @policy-export.json
```

## Cloner et personnaliser une policy

1. **Policy Management → [Policy] → Clone**
2. Modifier les critères (ex: abaisser le seuil CVSS de 9 à 7)
3. Ajouter un scope (ex: seulement namespace `prod-*`)
4. Changer l'enforcement (Inform → Enforce)
5. Save

---

## Résumé pour l'examen

> - +100 policies par défaut, organisées par lifecycle stage et catégorie
> - Policies **système** : non suppressibles, clonables
> - Modifier : scope, critères, enforcement, notifiers
> - 3 lifecycle stages : **Build, Deploy, Runtime** (une policy peut couvrir plusieurs)
> - Clone = meilleure pratique pour personnaliser sans casser l'original
