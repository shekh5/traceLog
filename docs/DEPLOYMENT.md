# Deploying TraceLog to Google Cloud

TraceLog deploys two Cloud Run services from one image:

- `patient`: the supervised reference agent.
- `dashboard`: the cockpit, SSE API, and in-process supervision loop.

The previous ADK/Vertex Agent Engine deployment is retired. The supervision loop is
provider-independent async Python running inside the dashboard service.

## Prerequisites

```bash
export PROJECT_ID="your-gcp-project"
export REGION="us-central1"
gcloud config set project "$PROJECT_ID"

gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com firestore.googleapis.com

gcloud artifacts repositories create tracelog \
  --repository-format=docker --location="$REGION"
gcloud firestore databases create --location="$REGION"

printf '%s' "$PHOENIX_API_KEY" | \
  gcloud secrets create phoenix-api-key --data-file=-
printf '%s' "$OPENAI_API_KEY" | \
  gcloud secrets create openai-api-key --data-file=-
openssl rand -hex 32 | \
  gcloud secrets create replay-shared-secret --data-file=-
openssl rand -hex 32 | \
  gcloud secrets create service-api-key --data-file=-
```

Retrieve the generated cockpit token when needed with
`gcloud secrets versions access latest --secret=service-api-key`; keep it out of
source control and browser persistence.

Grant the Cloud Run runtime service account `roles/secretmanager.secretAccessor` and
`roles/datastore.user`.

## First deployment

```bash
gcloud builds submit --config deploy/cloudbuild.yaml \
  --substitutions="_REGION=$REGION,_PHOENIX_BASE_URL=https://app.phoenix.arize.com"
```

Get the Patient URL and redeploy with the correct adapter endpoint:

```bash
PATIENT_URL="$(gcloud run services describe patient \
  --region "$REGION" --format='value(status.url)')/chat"

gcloud builds submit --config deploy/cloudbuild.yaml \
  --substitutions="_REGION=$REGION,_PATIENT_URL=$PATIENT_URL,_PHOENIX_BASE_URL=https://app.phoenix.arize.com"
```

Replace the Phoenix base URL with the URL for the target Phoenix space if it differs.

## Verify

```bash
DASHBOARD_URL="$(gcloud run services describe dashboard \
  --region "$REGION" --format='value(status.url)')"

curl --fail "$DASHBOARD_URL/healthz"
curl --fail "${PATIENT_URL%/chat}/healthz"
```

Or run the same retrying check used by Cloud Build and the scheduled canary:

```bash
scripts/smoke_test.sh "${PATIENT_URL%/chat}" "$DASHBOARD_URL"
```

The deploy pipeline injects `SERVICE_API_KEY` into both services. Enter that value in
the cockpit's password field before using **Drive the Patient** or **Self-evaluation**;
the browser keeps it only in React memory. API clients send it as
`Authorization: Bearer <SERVICE_API_KEY>`. Health endpoints and the read-only SSE feed
remain public for uptime monitoring and the live supervision display.

For the six-hour GitHub canary, set these repository variables under
**Settings > Secrets and variables > Actions > Variables**:

- `TRACELOG_PATIENT_URL`: Patient service base URL, without `/chat`.
- `TRACELOG_DASHBOARD_URL`: dashboard service base URL.

Also set the Actions secret `TRACELOG_SERVICE_API_KEY` to the same value stored in
Secret Manager. The canary first checks both health endpoints, then sends the canonical
Germany incident and fails unless all nine stages arrive over SSE and red-team
verification passes.

Then send the canonical incident from the cockpit and confirm:

1. The Patient trace appears in Phoenix.
2. TraceLog writes the diagnosis annotation and generated dataset.
3. A candidate prompt version is registered.
4. Replay and unseen holdout stages complete without hidden execution errors.
5. Red-team verification says `PASSED`; this requires every valid patched holdout to
   pass and at least `REDTEAM_MIN_VALID_HOLDOUTS` valid probes to complete.

## VM fallback

`deploy/vm_startup.sh` requires `GCP_PROJECT_ID` and `PHOENIX_BASE_URL`. Optional variables
are `GCP_REGION`, `ARTIFACT_REPOSITORY`, and `IMAGE_TAG`. Secrets are loaded from Secret
Manager at boot.

## Rename compatibility

Existing installations using old package, CLI, HTTP-header, Firestore collection, Phoenix
project, or Artifact Registry names require an explicit migration. Source-code rebranding
does not rename remote GitHub, GCP, Firestore, or Phoenix resources.
