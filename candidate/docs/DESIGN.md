# counter-api in production

**Cloud provider:** <!-- AWS / GCP / Azure -->

Assume `counter-api` is the first of about 20 similar services that product teams will ship onto this platform over
the next year. It needs to be highly available inside one region, and the counter must not be lost if a pod or a node
dies. Write about two pages. Short bullet points are fine. Be explicit about trade-offs and about what you'd defer.

## 1. Architecture

A diagram and a short description: accounts/projects, network layout, the cluster, how traffic gets from the internet
to a pod (DNS, TLS, load balancer, ingress), and where Redis lives.

## 2. Redis

Keep running Redis in the cluster, or use the provider's managed offering? Justify the choice. How does the app
connect to it (networking, auth, TLS)? What happens during a failover or maintenance window?

## 3. Identity and secrets

How do pods get cloud credentials without long-lived keys? How does the Redis password (or other secrets) get from a
secret store into the pod, and how is it rotated? Who and what can reach the cluster API?

## 4. Delivery

How does a change go from a merged pull request to production? Cover environments, how an image is built, scanned and
promoted, how manifests are deployed, and how you roll back. Push-based CI or GitOps? Why?

## 5. Observability

What would you measure, log and alert on for this service? Propose one or two SLOs. What pages a human at 3am, and
what doesn't?

## 6. Scaling, resilience and upgrades

Pod and node autoscaling, multiple availability zones, disruption handling. How do you upgrade the Kubernetes version
of the cluster without downtime?

## 7. Cost

A rough monthly estimate for the smallest production setup you'd be comfortable with. Where is most of the money going,
and what would you change first if you were asked to cut it by 30%?

## 8. Incident

It's 2am. You're paged: p99 latency on `counter-api` went from 20ms to 2s and some pods are restarting. Walk us through
your first 15 minutes.
