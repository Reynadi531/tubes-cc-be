# Yuki Agent Kubernetes Deployment

## Prerequisites
- Kubernetes cluster (minikube, k3s, GKE, EKS, AKS, etc.)
- kubectl configured to access cluster
- Docker (for building image)
- Ingress controller (optional, for external access)

## Quick Deploy

### 1. Build Container Image
```bash
docker build -t yuki-agent:latest .
```

### 2. Create Secret
**DO NOT commit secrets to git.** Use one of these methods:

**Method A: kubectl create (recommended)**
```bash
kubectl create secret generic yuki-secrets \
  --from-literal=GOOGLE_API_KEY=your-api-key \
  --from-literal=FRONTEND_URL=http://localhost:3001 \
  -n yuki
```

**Method B: Use template**
```bash
cp infra/k8s/secret.template.yaml infra/k8s/secret.yaml
# Edit secret.yaml with your values, then:
kubectl apply -f infra/k8s/secret.yaml
# DO NOT commit secret.yaml to git
```

### 3. Create TLS Secret (for HTTPS)
```bash
# Self-signed for development
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout tls.key -out tls.crt \
  -subj "/CN=yuki.local"

kubectl create secret tls yuki-tls \
  --cert=tls.crt --key=tls.key \
  -n yuki
```

### 4. Apply Manifests
```bash
# Apply in order
kubectl apply -f infra/k8s/namespace.yaml
kubectl apply -f infra/k8s/secret.yaml  # or use Method A above
kubectl apply -f infra/k8s/deployment.yaml
kubectl apply -f infra/k8s/service.yaml
kubectl apply -f infra/k8s/ingress.yaml
kubectl apply -f infra/k8s/network-policy.yaml
kubectl apply -f infra/k8s/pdb.yaml
```

### 5. Verify Deployment
```bash
# Check namespace
kubectl get namespace yuki

# Check pods
kubectl get pods -n yuki

# Check services
kubectl get svc -n yuki

# Check ingress
kubectl get ingress -n yuki

# View logs
kubectl logs -f deployment/yuki-agent -n yuki
```

### 6. Test API

**Port-forward for local testing:**
```bash
kubectl port-forward svc/yuki-agent 8000:8000 -n yuki &

curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Perkenalkan dirimu"}'
```

**Via Ingress:**
```bash
# Add to /etc/hosts
<ingress-ip> yuki.local

curl -X POST https://yuki.local/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "Halo Yuki!"}'
```

## Resource Configuration

| Resource | Request | Limit |
|----------|---------|-------|
| CPU | 100m | 500m |
| Memory | 128Mi | 512Mi |

## Security Features

| Feature | Status |
|---------|--------|
| Non-root container | ✓ |
| Read-only filesystem | ✓ |
| Drop all capabilities | ✓ |
| Seccomp profile | ✓ |
| Network policy | ✓ |
| TLS ingress | ✓ |

## Scaling Considerations

Current deployment uses `InMemorySessionService`. For horizontal scaling:

1. **Session Affinity**: Enable sticky sessions in Service:
   ```yaml
   spec:
     sessionAffinity: ClientIP
   ```

2. **External Session Store**: Use Redis or similar for session persistence (production recommended)

## Troubleshooting

### Pod not starting
```bash
kubectl describe pod -n yuki
kubectl logs -n yuki <pod-name>
```

### Secret issues
```bash
kubectl describe secret yuki-secrets -n yuki
```

### Ingress not working
```bash
kubectl describe ingress yuki-agent -n yuki
kubectl get ingressclass
```

## Files

```
infra/k8s/
├── namespace.yaml        # Namespace definition
├── secret.template.yaml  # Secret template (DO NOT commit with real values)
├── deployment.yaml       # Deployment with security context
├── service.yaml          # ClusterIP service
├── ingress.yaml          # Ingress with TLS
├── network-policy.yaml   # Network isolation
└── pdb.yaml              # Pod disruption budget
```
