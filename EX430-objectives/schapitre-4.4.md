# 4.4 — Manage network policies

## Rôle de RHACS

RHACS ne remplace pas les NetworkPolicies Kubernetes — il les **génère**, **simule** et **visualise** depuis le trafic observé.

## Visualiser les NetworkPolicies existantes

**Network → Network Graph → [namespace]**

```bash
oc get networkpolicies -n <namespace>
oc describe networkpolicy <name> -n <namespace>
```

## Générer des NetworkPolicies depuis RHACS

### Via l'UI

1. **Network → Network Graph → [namespace ou deployment]**
2. Bouton **Generate and Simulate Network Policies**
3. RHACS génère un YAML NetworkPolicy basé sur les flux observés
4. **Simulate** → voir l'impact avant application
5. **Apply** → appliquer directement sur le cluster

### Via roxctl

```bash
roxctl netpol generate \
  -e $ROX_ENDPOINT \
  --namespace production \
  --output-dir ./netpols/

oc apply -f ./netpols/
```

## Simulation de NetworkPolicy

Avant d'appliquer :
1. **Generate Policies → Simulate**
2. RHACS affiche :
   - Flux qui seraient **bloqués** (rouge)
   - Flux qui resteraient **autorisés** (vert)

## Exemple de NetworkPolicy générée

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: rhacs-netpol-frontend
  namespace: production
spec:
  podSelector:
    matchLabels:
      app: frontend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: nginx-ingress
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: backend
    ports:
    - protocol: TCP
      port: 3000
  - to:
    - namespaceSelector:
        matchLabels:
          kubernetes.io/metadata.name: kube-system
    ports:
    - protocol: UDP
      port: 53    # DNS toujours nécessaire !
```

---

## Résumé pour l'examen

> - RHACS **génère et simule** des NetworkPolicies depuis le trafic observé
> - Workflow : Observer → Générer → **Simuler** → Appliquer
> - `roxctl netpol generate` = génération CLI des NetworkPolicies
> - **Simuler avant d'appliquer** pour éviter de couper du trafic légitime
> - DNS (UDP 53 vers kube-dns) doit toujours être autorisé dans l'egress
