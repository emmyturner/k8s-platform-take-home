# Counter Platform: Take-Home Assessment

Thanks for taking the time to do this. It mirrors the work our platform team does every week: picking up a service
someone else wrote, getting it running on Kubernetes, making it safe to run in production, and deciding how it should
live in the cloud.

**Time box: 3–4 hours.** Please don't go over. Unfinished is fine. Tell us what you'd do next and we'll talk it
through in the follow-up. We care more about how you think than about how much you get done.

## The scenario

A product team built `counter-api`, a small Flask service that counts page hits in Redis. They wrote Kubernetes
manifests for it and say it "worked on my machine". It doesn't work anywhere else. They want it in production on a
managed Kubernetes service, and they've asked the platform team (you) to help.

```
namespace: counter

  client ──▶ Service counter-api ──▶ Deployment counter-api (2 pods)
                                             │
                                             ▼
                           Service redis ──▶ StatefulSet redis (1 pod + PVC)
```

```
app/                  Flask app and Dockerfile
k8s/base/             Kustomize base: every manifest for the service
k8s/overlays/local/   what `make deploy` applies to your local cluster
k8s/overlays/cloud/   empty for now (see Part 2)
docs/NOTES.md         your working notes (Parts 1 and 2)
docs/DESIGN.md        your cloud design (Part 3)
```

The app has three endpoints:

| Path       | Meaning                                                   |
|------------|-----------------------------------------------------------|
| `/`        | Increments the counter and returns `{"hits": N, "served_by": "<pod>"}` |
| `/healthz` | 200 if the process is up                                  |
| `/readyz`  | 200 if Redis is reachable, 503 otherwise                  |

It's configured with environment variables: `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_TLS`.

## Prerequisites

- Docker (Docker Desktop, colima, OrbStack and so on)
- `kubectl` 1.30 or newer (it includes Kustomize)
- [kind](https://kind.sigs.k8s.io/) **or** [minikube](https://minikube.sigs.k8s.io/)

Your cluster **must enforce NetworkPolicy**, because the manifests rely on it. `make cluster` sets this up for you by
installing Calico. If you'd rather use a cluster you already have, make sure its CNI enforces NetworkPolicy.

```sh
make cluster                         # kind, 1 control plane + 2 workers, Calico
make cluster CLUSTER_TOOL=minikube   # or minikube with Calico
```

If you use minikube, pass `CLUSTER_TOOL=minikube` to every `make` command.

## Part 1: Get it running (about 90 minutes)

```sh
make up      # build the image, load it into the cluster, kubectl apply -k k8s/overlays/local, restart the API
make smoke   # call the API 10 times from inside the cluster
make status
```

It's broken. There are several problems, in the Dockerfile and the manifests, and fixing one often reveals the next.

**You're done with Part 1 when:**

- `make smoke` prints 10 responses with an increasing `hits` count, served by more than one pod, and
- every pod in the `counter` namespace is `Running` and `Ready`, and none restarts in the 5 minutes after your last
  deploy.

**Ground rules:**

- **Fix problems at the root. Don't route around them.** Deleting the NetworkPolicies, removing the pod
  `securityContext`, or running as root would make things "work", but it doesn't count. If you think a control is
  wrong, fix the control.
- You may change anything in `app/` or `k8s/`. You shouldn't need to change the app's Python logic.
- For each problem, write a short entry in [`docs/NOTES.md`](docs/NOTES.md): the symptom, how you diagnosed it (the
  commands you ran and what told you the answer), and the fix. **This write-up is the most important part of Part 1.**
- Please commit as you go (one commit per fix is ideal). Your git history helps us follow your reasoning.

## Part 2: Make it production-ready (about 60 minutes)

The service now runs. Would you be comfortable putting it in front of customers? Change the manifests (and the
Dockerfile, if needed) so that you would be. At a minimum:

1. **Pod security.** The `counter` namespace enforces the
   [`restricted` Pod Security Standard](https://kubernetes.io/docs/concepts/security/pod-security-standards/), and
   everything in it still runs.
2. **Health checks.** The probes reflect what each one is for. Think about what happens to the API when Redis has a
   bad minute.
3. **Resources.** Requests and limits you can justify.
4. **Availability.** The API keeps serving through a rolling deploy, and through a drain of a worker node that runs
   API pods but not Redis (`kubectl drain <node> --ignore-daemonsets --delete-emptydir-data` on the two-worker kind
   cluster). Redis is a single pod here. What happens when *its* node is drained is worth a few lines in your notes.

Then pick **at least one** of these. Your choice tells us something too:

5. **Autoscaling.** The API scales on load. (On kind or minikube you'll need
   [metrics-server](https://github.com/kubernetes-sigs/metrics-server) to see it work. The manifests alone are fine.)
6. **Cloud overlay.** `k8s/overlays/cloud` describes what's different in a real cloud environment. It only has to
   render with `kubectl kustomize k8s/overlays/cloud`, and should match what you propose in Part 3.

In `docs/NOTES.md`, explain what you changed and why. Also list anything you chose **not** to do, and why.

## Part 3: Cloud platform design (about 45 minutes)

Write [`docs/DESIGN.md`](docs/DESIGN.md): how you would run `counter-api` in production on **AWS, GCP or Azure**
(your choice). The template has the questions we'd like answered. Aim for about two pages, and keep it concise. A
diagram (ASCII or Mermaid is fine) is very welcome. You don't need a cloud account, and you shouldn't spend any money.

## Part 4: Stretch (optional)

Only if you have time left inside the time box. Pick at most one. Skipping this costs you nothing.

- **Terraform** for the core cloud infrastructure from Part 3. It must pass `terraform init -backend=false` and
  `terraform validate`. Don't apply it.
- **CI**: a GitHub Actions workflow that builds the image, validates the manifests, starts kind, deploys, and runs the
  smoke test.
- **Observability**: expose Prometheus metrics from the app and add the manifests to scrape them and alert on them.

## Submitting

Send us a link to a private git repository (or a zip of it, **including** `.git`). It should contain:

- your fixed and improved `app/` and `k8s/`
- `docs/NOTES.md` and `docs/DESIGN.md`
- roughly how long you spent, at the bottom of `NOTES.md`

You may use any resources you like, including documentation, search and AI assistants. In the follow-up conversation
we'll ask you to walk us through your changes, so make sure you can explain and defend every line.

In the follow-up (about 60 minutes) we'll go through your submission together, and change a few things live.

Questions about the exercise itself are welcome. Just reply to the email you received this in.
