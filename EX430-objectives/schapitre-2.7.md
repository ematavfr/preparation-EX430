# 2.7 — Manage vulnerability notifications

## Principe

RHACS peut notifier des équipes externes lorsque des vulnérabilités sont détectées, via des **intégrations de notification** couplées à des **policies** ou des **rapports de vulnérabilité**.

## Intégrations de notification disponibles

| Type | Usage |
|---|---|
| **Email** | Notification par email (SMTP) |
| **Slack** | Message dans un channel Slack |
| **PagerDuty** | Création d'incident PagerDuty |
| **Jira** | Création de ticket Jira |
| **Splunk** | Envoi d'événements vers Splunk |
| **Sumo Logic** | Idem |
| **Google Cloud SCC** | Security Command Center |
| **Microsoft Sentinel** | SIEM Microsoft |
| **Webhook générique** | HTTP POST vers n'importe quel endpoint |

## Configurer une intégration (ex: Email)

### Via l'UI

1. **Platform Configuration → Integrations → Notifiers → Generic Email**
2. Renseigner :

```
Name: email-securite
Server: smtp.company.com:587
SMTP username: rhacs@company.com
SMTP password: ****
From: rhacs-alerts@company.com
To: security-team@company.com
TLS: STARTTLS
```

3. **Test → Save**

### Webhook générique

```bash
# Payload envoyé par RHACS au webhook lors d'une violation :
{
  "summary": "Policy violated: Fixable CVSS >= 9",
  "alertId": "abc-123",
  "policy": {"name": "...", "severity": "CRITICAL_SEVERITY"},
  "deployment": {"name": "myapp", "namespace": "prod"},
  "violations": [...]
}
```

## Associer un notifier à une policy de vulnérabilité

1. **Platform Configuration → Policy Management → [Policy] → Edit**
2. Onglet **Actions** → **Notifiers** → sélectionner l'intégration
3. Sauvegarder

Désormais, chaque violation de cette policy déclenche une notification.

## Notifier via les rapports de vulnérabilité

1. **Vulnerability Management → Reporting → [Report] → Edit**
2. Section **Delivery** : sélectionner le notifier email
3. Le rapport est envoyé selon le schedule configuré

## Notifications par CVE Watchlist

1. Ajouter une CVE en watchlist : **Vulnerability Management → [CVE] → Add to watchlist**
2. Configurer le notifier associé à la watchlist
3. Notification déclenchée dès qu'une image avec cette CVE apparaît

## Tester une intégration

```bash
# Via UI : Integrations → [notifier] → Test
# Via API :
curl -sk -X POST "$ROX_ENDPOINT/v1/notifiers/<id>/test" \
  -H "Authorization: Bearer $TOKEN"
```

## Filtrer les notifications

Pour éviter le bruit, utiliser les **scopes** de policy :

```yaml
# Dans une policy : restreindre aux namespaces de prod
policyScope:
  - cluster: ocp-prod
    namespace: "prod-.*"
```

---

## Résumé pour l'examen

> - Notifiers configurés dans : **Platform Configuration → Integrations → Notifiers**
> - Types clés : Email, Slack, Webhook générique, Jira, PagerDuty
> - Associer un notifier à une **policy** → notification sur violation
> - Associer un notifier à un **rapport** → envoi planifié
> - **CVE Watchlist** → alerte continue sur une CVE précise
> - Tester systématiquement l'intégration avant de sauvegarder
