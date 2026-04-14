# 6.3 — Integrate an OIDC provider for authentication

## Principes

RHACS supporte l'authentification externe via **OIDC** (OpenID Connect). Cela permet d'utiliser les identités existantes (Keycloak, Dex, OpenShift OAuth, Okta, Azure AD...) au lieu du compte admin local.

## Providers OIDC supportés

| Provider | Type dans RHACS |
|---|---|
| **OpenShift OAuth** | OpenShift Auth Provider (natif) |
| **Keycloak** | OIDC |
| **Dex** | OIDC |
| **Okta** | OIDC |
| **Azure AD** | OIDC |
| **GitHub** | GitHub (type dédié) |
| **Google Workspace** | OIDC |
| **LDAP** | Non supporté directement (passer par Dex) |
| **SAML 2.0** | SAML (type dédié) |

## Configurer un Auth Provider OIDC

### Via l'UI

1. **Platform Configuration → Access Control → Auth Providers → Add**
2. Sélectionner **OIDC**
3. Renseigner :

```
Name: Keycloak Production
Issuer: https://sso.company.com/realms/rhacs
Client ID: rhacs-client
Client Secret: **** (si confidential client)
Mode: Auto-select (ou Fragment / Post / Query)
```

4. Configurer le **Role Mapping** :

```
Minimum access role: Analyst
Rule: 
  Key:   email
  Value: .*@company.com
  Role:  Admin
```

5. **Save** → tester la connexion

### Via OpenShift OAuth (intégration native)

```bash
# RHACS détecte automatiquement l'OpenShift OAuth si déployé sur OCP
# Platform Configuration → Access Control → Auth Providers
# → "OpenShift Auth" est déjà disponible
```

## Configuration côté IdP (ex: Keycloak)

```
Client ID: rhacs-client
Client Type: confidential (ou public)
Valid Redirect URIs: https://<central-url>/sso/providers/oidc/callback
Web Origins: https://<central-url>

Claims requis : email, name (ou preferred_username)
```

## Role Mapping (règles d'attribution des rôles)

RHACS mappe les claims OIDC vers ses rôles internes :

| Rôle RHACS | Permissions |
|---|---|
| **Admin** | Accès complet |
| **Analyst** | Lecture seule |
| **Continuous Integration** | Scan d'images (CI/CD) |
| **Network Graph Viewer** | Lecture network graph |
| **Sensor Creator** | Créer des init bundles |
| **Vulnerability Management Approver** | Approuver les deferrals |

Exemple de règle de mapping :

```
Claim: groups
Value: rhacs-admins     → Role: Admin
Value: rhacs-viewers    → Role: Analyst
Value: ci-bots          → Role: Continuous Integration
```

## Vérifier l'authentification

```bash
# Tester le login avec l'IdP configuré
# UI : ouvrir une fenêtre privée → sélectionner le provider OIDC
# Vérifier le rôle attribué : profil utilisateur en haut à droite
```

## Tokens API (non OIDC)

Pour les accès programmatiques (CI/CD, scripts) :

```bash
# Créer un token API (indépendant de l'OIDC)
# Platform Configuration → Integrations → API Tokens → Generate Token
# Rôle : Continuous Integration (ou minimum requis)

export ROX_API_TOKEN="eyJ..."
roxctl -e $ROX_ENDPOINT central whoami
```

## Machine Access Tokens (court-terme, OIDC natif)

Pour les pipelines CI/CD modernes, RHACS supporte les **machine access tokens** — des tokens OIDC court-terme émis par des cloud providers :

```
Platform Configuration → Integrations → Authentication Tokens → Machine access configuration
→ Create configuration
```

Types supportés :
| Type | Issuer |
|---|---|
| **Generic** | Tout issuer OIDC arbitraire |
| **GitHub Actions** | `token.actions.githubusercontent.com` |
| **Google Cloud** | Google Cloud Identity Platform |
| **Azure** | Microsoft Entra ID |

> Avantage : pas de credentials statiques — le token est éphémère et émis par le cloud provider. Recommandé sur AWS/GCP/Azure pour les pipelines CI/CD. Plus sécurisé que les API tokens à longue durée de vie.

---

## Résumé pour l'examen

> - Auth Providers : **Platform Configuration → Access Control → Auth Providers**
> - Types supportés : OIDC, OpenShift Auth, GitHub, SAML
> - Configuration clé : Issuer URL + Client ID + Client Secret + Redirect URI
> - **Role Mapping** : claim OIDC → rôle RHACS
> - OpenShift OAuth : disponible nativement sans configuration extra sur OCP
> - Tokens API = pour CI/CD, indépendants de l'OIDC
