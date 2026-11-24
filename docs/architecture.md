# Architecture

## Overview

The platform has four parts that each do one job.

| Part | Tool | Job |
|---|---|---|
| Infrastructure | Terraform | Creates the Azure resource group and the AKS cluster. State lives in an Azure Storage account, so it is not tied to one laptop. |
| Build and release | GitHub Actions | Runs the tests, builds the image, pushes it to GHCR, and writes the new image tag into `helm/demo-app/values.yaml`. |
| Delivery | Argo CD | Watches this repository. When the Helm values change, it syncs the chart to the cluster. The cluster state follows Git. |
| Observability | Prometheus, Grafana | Scrape the app, evaluate the SLO rules, and show the result. |

## Delivery flow

1. A change to `app/` is pushed to `main`.
2. The pipeline runs the tests, builds the image, pushes `ghcr.io/<owner>/aks-gitops-platform/demo-app:<short-sha>`, then commits the new tag to `helm/demo-app/values.yaml`.
3. Argo CD sees the new commit and rolls out the new image to the `demo` namespace.
4. A change to `helm/demo-app/values.yaml` alone, such as `failureRate`, is picked up the same way, without a new image.

The pipeline only runs for changes under `app/`. Its own deploy commit changes only the Helm values, so it does not trigger itself in a loop.

## Observability and SLO

The app exposes `/metrics`. A `ServiceMonitor` tells Prometheus to scrape it. Two recording rules turn raw request counts into an error ratio and a burn rate against a 99% objective. Two alerts sit on top: a warning when more than 5% of requests fail, and a critical alert for a fast error-budget burn.

## Design choices

- **Free-tier control plane.** Only the nodes cost money, so the lab is cheap and easy to destroy.
- **Git as the source of truth.** Nobody runs `kubectl apply` for the app. A rollback is a `git revert`.
- **Remote state.** Terraform state is in Azure Storage with its own resource group, kept apart from the cluster so it survives a teardown.
- **Failure injection through config.** The failure rate is a Helm value, so a drill is a normal Git change that goes through the same delivery path as any other.
