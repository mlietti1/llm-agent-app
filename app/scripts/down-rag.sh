#!/usr/bin/env bash
# Remove the rag-assistant stack from the cluster.
# Keeps the kind cluster, Argo CD and the monitoring stack.
# Run it from the repository root:  ./scripts/down-rag.sh
set -euo pipefail

ARGOCD_NS="${ARGOCD_NS:-argocd}"
APP_NAME="rag-assistant"

# 1. Delete the Argo CD Application first. Otherwise automated sync (selfHeal)
#    would recreate whatever we delete. The finalizer makes Argo CD delete the
#    application's resources (Deployment, StatefulSet, Services) with it.
if kubectl -n "$ARGOCD_NS" get application "$APP_NAME" >/dev/null 2>&1; then
  kubectl -n "$ARGOCD_NS" patch application "$APP_NAME" --type merge \
    -p '{"metadata":{"finalizers":["resources-finalizer.argocd.argoproj.io"]}}'
  kubectl -n "$ARGOCD_NS" delete application "$APP_NAME" --wait=true
fi

# 2. Remove what Argo CD does not own: the Secret and the Qdrant volume.
#    The vectors are rebuilt from docs/ by the ingest step in up-rag.sh.
kubectl delete namespace rag --ignore-not-found

echo "rag-assistant removed. Cluster, Argo CD and monitoring are untouched."
