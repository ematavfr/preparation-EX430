# 2.6 — Interpret vulnerability results

## Lire un résultat de scan d'image

```
Image: registry.io/myapp:1.0
Total CVEs: 47
├── Critical:   3  (2 fixable)
├── Important:  12 (8 fixable)
├── Moderate:   25
└── Low:        7
```

### Détail d'une CVE

| Champ | Signification |
|---|---|
| **CVE ID** | CVE-2024-21626 |
| **Component** | runc 1.1.6 |
| **Fixed in** | runc 1.1.12 |
| **CVSS v3** | 8.6 (High) |
| **RHACS Severity** | Critical |
| **Vector** | AV:L/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H |
| **Published** | 2024-01-31 |
| **Fixable** | Yes |

## CVSS et mapping sévérité RHACS

| CVSS v3 Score | Sévérité NVD | Sévérité RHACS |
|---|---|---|
| 9.0 – 10.0 | Critical | Critical |
| 7.0 – 8.9 | High | Important |
| 4.0 – 6.9 | Medium | Moderate |
| 0.1 – 3.9 | Low | Low |

> RHACS utilise la terminologie Red Hat (Important vs High) — important pour l'exam !

## Vecteur CVSS — comprendre l'exploitabilité

```
CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H = 9.8 (Critical)
```

| Métrique | Valeur | Signification |
|---|---|---|
| **AV** (Attack Vector) | N=Network, A=Adjacent, L=Local, P=Physical | Comment l'attaquant accède |
| **AC** (Attack Complexity) | L=Low, H=High | Difficulté d'exploitation |
| **PR** (Privileges Required) | N=None, L=Low, H=High | Droits nécessaires |
| **UI** (User Interaction) | N=None, R=Required | Interaction humaine requise |

## Fixabilité — décision de remédiation

```
Fixable → Prioriser : mettre à jour le package
Not fixable → Mitigations alternatives ou deferral justifié
```

**Stratégie de priorisation :**
1. Critical + Fixable + Déployé en prod → remédiation immédiate
2. Critical + Not fixable → évaluer mitigations (réseau, WAF, deferral)
3. Important + Fixable → remédiation dans le sprint suivant
4. Moderate/Low → backlog, traité lors du prochain rebuild

## Lire les résultats depuis roxctl

```bash
roxctl image scan --image=registry.io/myapp:1.0 \
  -e $ROX_ENDPOINT --output=json | jq '
  .result.vulnerabilities[] |
  select(.severity == "CRITICAL_VULNERABILITY_SEVERITY") |
  {cve: .cveId, component: .componentName, fixedIn: .fixedByVersion}
'
```

## Résultats dans l'UI — Vulnerability Management

### Vue Image

- **Risk score** de l'image (0-1000, calculé par RHACS)
- Liste des CVE avec filtres
- Onglet **Components** : quels packages sont vulnérables
- Onglet **Deployments** : où cette image est déployée

### Vue Deployment

- CVE héritées de toutes les images du déploiement
- **Risk factors** : nombre de CVE, exposition réseau, privileges...
- **Risk score** global du déploiement

## SBOM (Software Bill of Materials)

RHACS génère implicitement un SBOM lors du scan :
- Liste de tous les packages/composants de l'image
- Visible dans l'UI sous **Components** d'une image

---

## Résumé pour l'examen

> - Sévérité RHACS : **Critical / Important / Moderate / Low** (Important = High CVSS)
> - CVSS score : 9-10 = Critical, 7-8.9 = Important, 4-6.9 = Moderate, <4 = Low
> - Prioriser : **Critical + Fixable + image déployée en prod**
> - Fixable = rebuild avec la version corrigée du package
> - `jq` sur le JSON de `roxctl image scan` pour filtrer programmatiquement
