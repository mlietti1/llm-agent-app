#!/usr/bin/env bash
# Bring the rag-assistant stack up on an existing kind cluster that already runs Argo CD.
# Run it from the repository root:  ./scripts/up-rag.sh
set -euo pipefail

# ---- Edit these if needed -------------------------------------------------
CLUSTER="${CLUSTER:-$(kind get clusters | head -1)}"
APP_IMAGE="rag-assistant:0.1.1"                 # must match deploy/rag-assistant/app.yaml
QDRANT_IMAGE="qdrant/qdrant:vX.Y.Z"             # must match deploy/rag-assistant/qdrant.yaml
ENV_FILE="app/.env"                             # holds LLM_API_KEY (never committed)
APPLICATION="deploy/rag-assistant-application.yaml"
# ---------------------------------------------------------------------------

if [ -z "$CLUSTER" ]; then
  echo "No kind cluster found. Create the platform first (terraform apply)." >&2
  exit 1
fi

kubectl config use-context "kind-${CLUSTER}" >/dev/null

if ! kubectl get crd applications.argoproj.io >/dev/null 2>&1; then
  echo "Argo CD is not installed in cluster '${CLUSTER}'. Run terraform apply first." >&2
  exit 1
fi

# 1. Images must exist locally, then be loaded into the kind nodes
if ! docker image inspect "$APP_IMAGE" >/dev/null 2>&1; then
  echo "Image $APP_IMAGE not found locally. Build it first:  docker build -t $APP_IMAGE app/" >&2
  exit 1
fi
docker image inspect "$QDRANT_IMAGE" >/dev/null 2>&1 || docker pull "$QDRANT_IMAGE"

echo "Loading images into kind cluster '${CLUSTER}'..."
kind load docker-image "$APP_IMAGE" "$QDRANT_IMAGE" --name "$CLUSTER"

# 2. Namespace and Secret (the API key lives only in the Secret, never in Git)
kubectl get namespace rag >/dev/null 2>&1 || kubectl create namespace rag

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a
kubectl -n rag create secret generic llm-credentials \
  --from-literal=LLM_API_KEY="$LLM_API_KEY" \
  --dry-run=client -o yaml | kubectl apply -f -

# 3. Hand over to Argo CD
kubectl apply -f "$APPLICATION"

wait_for() {
  local selector="$1"
  until [ -n "$(kubectl -n rag get pods -l "$selector" -o name 2>/dev/null)" ]; do
    sleep 3
  done
  kubectl -n rag wait --for=condition=Ready pod -l "$selector" --timeout=300s
}

echo "Waiting for Argo CD to create and start the pods..."
wait_for app=qdrant
wait_for app=rag-assistant

# 4. Qdrant is empty after a fresh deployment: ingest the documents
echo "Ingesting documents into the in-cluster Qdrant..."
kubectl -n rag port-forward svc/qdrant 6335:6333 >/dev/null 2>&1 &
PF_PID=$!
trap 'kill $PF_PID 2>/dev/null || true' EXIT
sleep 3
( cd app && QDRANT_URL=http://localhost:6335 PYTHONPATH=src .venv/bin/python -m ragapp.ingest ../docs )

echo
echo "Done. Try it with:"
echo "  kubectl -n rag port-forward svc/rag-assistant 8002:8000"
echo "  curl -X POST localhost:8002/ask -H 'Content-Type: application/json' -d '{\"question\":\"...\"}'"
