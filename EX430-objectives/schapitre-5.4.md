# 5.4 — Configure tailored profiles

## Concept

Un **TailoredProfile** permet de **personnaliser un profil de conformité existant** en :
- Désactivant des règles qui ne s'appliquent pas (faux positifs, exceptions)
- Activant des règles supplémentaires
- Modifiant les valeurs de certaines variables (ex: longueur minimale de mot de passe)

## Créer un TailoredProfile

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: TailoredProfile
metadata:
  name: ocp4-cis-custom
  namespace: openshift-compliance
spec:
  title: "CIS OCP4 - Profil personnalisé production"
  description: "CIS OCP4 avec exceptions approuvées pour notre environnement"
  extends: ocp4-cis              # Profil de base
  
  disableRules:
    - name: ocp4-api-server-audit-log-path
      rationale: "Géré par notre SIEM externe, audit log désactivé intentionnellement"
    - name: ocp4-node-authorization-mode-rbac
      rationale: "Contrôle N/A sur notre version OCP"
  
  enableRules:
    - name: ocp4-api-server-tls-private-key
      rationale: "Requis par notre politique de sécurité interne"
  
  setValues:
    - name: ocp4-var-password-minlen
      rationale: "Notre politique impose 14 caractères minimum"
      value: "14"
```

```bash
oc apply -f tailored-profile.yaml
oc get tailoredprofiles -n openshift-compliance
```

## Lister les règles disponibles

```bash
# Voir toutes les règles du profil de base
oc get rules.compliance -n openshift-compliance | grep ocp4-cis | head -20

# Détail d'une règle
oc describe rule.compliance ocp4-api-server-audit-log-path -n openshift-compliance
```

## Lister les variables configurables

```bash
# Variables du profil
oc get variables.compliance -n openshift-compliance | grep ocp4

# Valeurs possibles d'une variable
oc describe variable.compliance ocp4-var-password-minlen -n openshift-compliance
```

## Utiliser le TailoredProfile dans un ScanSettingBinding

```yaml
apiVersion: compliance.openshift.io/v1alpha1
kind: ScanSettingBinding
metadata:
  name: custom-cis-scan
  namespace: openshift-compliance
spec:
  profiles:
  - apiGroup: compliance.openshift.io/v1alpha1
    kind: TailoredProfile                  # Utiliser TailoredProfile, pas Profile
    name: ocp4-cis-custom
  settingsRef:
    apiGroup: compliance.openshift.io/v1alpha1
    kind: ScanSetting
    name: default
```

```bash
oc apply -f scansettingbinding-custom.yaml
```

## Vérifier que le profil personnalisé est utilisé

```bash
oc get compliancescans -n openshift-compliance
# Le scan doit référencer ocp4-cis-custom comme profil

oc get compliancecheckresults -n openshift-compliance \
  -l compliance.openshift.io/suite=custom-cis-scan
```

## Bonnes pratiques

```
1. Toujours documenter le rationale de chaque règle désactivée
2. Soumettre les TailoredProfiles à revue avant production
3. Conserver le TailoredProfile dans git (GitOps)
4. Re-évaluer les exceptions à chaque mise à jour du profil de base
```

---

## Résumé pour l'examen

> - **TailoredProfile** = personnalisation d'un profil existant (extends: <profil-base>)
> - 3 opérations : `disableRules`, `enableRules`, `setValues`
> - Utiliser `kind: TailoredProfile` dans le ScanSettingBinding (pas `Profile`)
> - Namespace : `openshift-compliance`
> - Toujours documenter le `rationale` de chaque exception
> - `oc get rules.compliance` et `oc get variables.compliance` pour explorer les options disponibles
