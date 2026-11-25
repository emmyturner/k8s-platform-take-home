# Local workflow for the counter take-home.
#   make cluster   create a local cluster (kind by default; CLUSTER_TOOL=minikube also works)
#   make up        build the image, load it into the cluster, apply the manifests, restart the API
#   make smoke     call the API from inside the cluster
#   make destroy   delete the local cluster

CLUSTER_TOOL ?= kind
CLUSTER_NAME ?= counter
IMAGE        ?= counter-api:dev
OVERLAY      ?= k8s/overlays/local
NAMESPACE    ?= counter

CALICO_MANIFEST ?= https://raw.githubusercontent.com/projectcalico/calico/v3.29.1/manifests/calico.yaml

.DEFAULT_GOAL := help
.PHONY: help cluster build load deploy up smoke status destroy

help: ## Show this help
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*## "}; {printf "  %-10s %s\n", $$1, $$2}'

cluster: ## Create a local cluster that enforces NetworkPolicy
ifeq ($(CLUSTER_TOOL),kind)
	kind create cluster --name $(CLUSTER_NAME) --config kind-config.yaml
	kubectl apply -f $(CALICO_MANIFEST)
	kubectl -n kube-system rollout status daemonset/calico-node --timeout=300s
else ifeq ($(CLUSTER_TOOL),minikube)
	minikube start -p $(CLUSTER_NAME) --cni=calico
else
	$(error CLUSTER_TOOL must be kind or minikube)
endif
	kubectl wait --for=condition=Ready nodes --all --timeout=300s

build: ## Build the API image
	docker build -t $(IMAGE) app

load: ## Build the image and make it available to the cluster
ifeq ($(CLUSTER_TOOL),kind)
	docker build -t $(IMAGE) app
	kind load docker-image $(IMAGE) --name $(CLUSTER_NAME)
else
	minikube image build -t $(IMAGE) -p $(CLUSTER_NAME) app
endif

deploy: ## Apply the manifests for OVERLAY
	kubectl apply -k $(OVERLAY)

# The image tag never changes, so pods only pick up a rebuilt image when they are recreated.
up: load ## Build, load, apply, and restart the API so it runs the new image
	-kubectl apply -k $(OVERLAY)
	@kubectl -n $(NAMESPACE) rollout restart deployment/counter-api 2>/dev/null || true

smoke: ## Call the API 10 times from a pod inside the cluster
	@kubectl delete pod counter-smoke --ignore-not-found --wait=true >/dev/null
	kubectl run counter-smoke --rm -i --quiet --restart=Never \
	  --image=curlimages/curl:8.11.1 --command -- \
	  sh -c 'for i in $$(seq 1 10); do curl -fsS --max-time 3 http://counter-api.$(NAMESPACE).svc.cluster.local/ || exit 1; echo; done'

status: ## Show what is running in the namespace
	kubectl -n $(NAMESPACE) get pods,svc,endpointslices,pvc -o wide

destroy: ## Delete the local cluster
ifeq ($(CLUSTER_TOOL),kind)
	kind delete cluster --name $(CLUSTER_NAME)
else
	minikube delete -p $(CLUSTER_NAME)
endif
