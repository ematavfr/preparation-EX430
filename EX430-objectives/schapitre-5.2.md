# 5.2 — Manage compliance

## Vue Compliance dans RHACS

Navigation : **Compliance** (menu principal)

RHACS affiche les résultats de conformité en les corrélant avec :
- Les résultats du **Compliance Operator** (scans OpenSCAP)
- Sa propre évaluation des **policies RHACS** mappées aux contrôles

## Terminologie (DO430)

| Terme | Définition |
|---|---|
| **Control** | Ligne d'un standard évaluée par un auditeur (ex: CIS-1.1.1) |
| **Check** | Test unitaire effectué pour évaluer un contrôle — 1 contrôle peut avoir **plusieurs checks** |

> Les scores RHACS sont calculés au niveau des **controls**. Les résultats détaillés sont au niveau des **checks**.

## Statuts possibles d'un check (Operating guide 4.6)

| Statut | Signification |
|---|---|
| **Pass** | Le check a réussi |
| **Fail** | Le check a échoué |
| **Not Applicable** | Check ignoré — non applicable à cet environnement |
| **Info** | Données collectées, mais RHACS ne peut pas déterminer Pass ou Fail |
| **Error** | Échec technique du check (problème d'exécution, pas de conformité) |
| **Manual** | Intervention manuelle requise pour évaluer ce contrôle |

> **Point clé examen** : Ne pas confondre **Error** (problème technique d'exécution du check) et **Fail** (check exécuté correctement mais non conforme). **Manual** = contrôle non automatisable.

## Standards supportés

| Standard | Description |
|---|---|
| **CIS Kubernetes** | CIS Benchmark pour Kubernetes |
| **CIS OpenShift** | CIS Benchmark pour OCP 4 |
| **NIST SP 800-53** | Framework US gouvernemental |
| **PCI-DSS** | Payment Card Industry |
| **HIPAA** | Healthcare (US) |
| **SOC 2** | Controls d'organisation de services |

## Vue Dashboard Compliance

```
Compliance → Dashboard
├── Overall compliance score (%)
├── Par standard : score de conformité
├── Par cluster : score
└── Par namespace : score
```

## Drill-down par standard

1. **Compliance → [Standard CIS OCP4]**
2. Liste des **contrôles** avec statut : Pass / Fail / N/A
3. Cliquer sur un contrôle → détail des ressources concernées
4. Voir quelles policies RHACS ou checks OpenSCAP couvrent ce contrôle

## Intégration avec le Compliance Operator

RHACS importe automatiquement les résultats du Compliance Operator si :
1. Le cluster est sécurisé par RHACS (SecuredCluster déployé)
2. Le Compliance Operator est installé sur ce cluster
3. Des scans ont été exécutés (ScanSettingBinding actif)

```bash
# Vérifier que les résultats sont bien remontés dans RHACS
# UI : Compliance → [standard] → voir les résultats avec source "Compliance Operator"
```

## Remédiation automatique

Le Compliance Operator peut appliquer automatiquement des remédiations pour certains contrôles :

```bash
# Voir les remédications disponibles
oc get complianceremediations -n openshift-compliance

# Appliquer une remédiation
oc patch complianceremediation/<name> -n openshift-compliance \
  --type=merge -p '{"spec":{"apply":true}}'
```

> **Attention** : appliquer des remédiations automatiques peut modifier la config du cluster — tester en non-prod d'abord.

## Gestion des exceptions de conformité

Pour les contrôles qui ne s'appliquent pas :

```bash
# Marquer un check comme N/A (not applicable)
oc annotate compliancecheckresult/<check-name> -n openshift-compliance \
  compliance.openshift.io/check-status=NOT-APPLICABLE
```

## Surveiller la régression de conformité

RHACS montre l'évolution du score dans le temps :
- **Compliance → [Standard] → Trend** : graphe de progression
- Permettre de détecter si une mise à jour du cluster a réduit la conformité

---

## Résumé pour l'examen

> - Compliance Dashboard : score global par standard, cluster, namespace
> - Standards : CIS K8s, CIS OCP4, NIST 800-53, PCI-DSS, HIPAA, SOC 2
> - **Control** = ligne du standard ; **Check** = test unitaire (1 control → N checks)
> - RHACS importe automatiquement les résultats du Compliance Operator
> - Drill-down : standard → contrôle → ressources concernées
> - Remédiation automatique disponible via `ComplianceRemediation` CR
> - Surveiller la tendance (Trend) pour détecter les régressions
