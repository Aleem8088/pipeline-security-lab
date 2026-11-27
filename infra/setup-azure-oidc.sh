#!/usr/bin/env bash
# Creates the minimum needed for GitHub Actions to log in to Azure with OIDC (no stored password):
#   - an empty resource group (free)
#   - an Entra app registration + service principal (free)
#   - a federated credential that trusts ONLY the "production" environment of this one repo
#   - the Reader role on that resource group only
# Run it with the Azure CLI already logged in to the intended (personal) subscription.
# Usage: infra/setup-azure-oidc.sh <github-owner> <repo> <owner-id> <repo-id>
set -euo pipefail
export MSYS_NO_PATHCONV=1   # Git Bash on Windows would otherwise mangle /subscriptions/... paths

OWNER="${1:?github owner}"; REPO="${2:?repo}"; OWNER_ID="${3:?github owner id}"; REPO_ID="${4:?github repo id}"
RG="rg-pipeline-lab"; LOCATION="centralindia"; APP="pipeline-security-lab-oidc"

SUB_ID=$(az account show --query id -o tsv)
TENANT_ID=$(az account show --query tenantId -o tsv)

az group create -n "$RG" -l "$LOCATION" -o none
APP_ID=$(az ad app list --display-name "$APP" --query "[0].appId" -o tsv)
if [ -z "$APP_ID" ]; then APP_ID=$(az ad app create --display-name "$APP" --query appId -o tsv); fi
az ad sp show --id "$APP_ID" -o none 2>/dev/null || az ad sp create --id "$APP_ID" -o none

# Repos created after 2026-07-15 use the immutable subject format (owner and repo IDs).
SUBJECT="repo:${OWNER}@${OWNER_ID}/${REPO}@${REPO_ID}:environment:production"
FEDCRED=$(mktemp)
cat > "$FEDCRED" <<JSON
{"name":"github-production","issuer":"https://token.actions.githubusercontent.com","subject":"${SUBJECT}","audiences":["api://AzureADTokenExchange"]}
JSON
# The Windows Azure CLI needs a Windows-style path; plain POSIX paths are fine elsewhere.
FEDCRED_ARG="$FEDCRED"; if command -v cygpath >/dev/null 2>&1; then FEDCRED_ARG=$(cygpath -w "$FEDCRED"); fi
EXISTING=$(az ad app federated-credential list --id "$APP_ID" --query "[?name=='github-production'].name" -o tsv)
if [ -z "$EXISTING" ]; then az ad app federated-credential create --id "$APP_ID" --parameters "$FEDCRED_ARG" -o none; fi
rm -f "$FEDCRED"

# Use the service principal's object id: assigning by app id can fail right after creation.
SP_ID=$(az ad sp show --id "$APP_ID" --query id -o tsv)
az role assignment create --assignee-object-id "$SP_ID" --assignee-principal-type ServicePrincipal   --role Reader --scope "/subscriptions/${SUB_ID}/resourceGroups/${RG}" -o none

echo "Done. Store these three as GitHub *secrets* (identifiers, not credentials):"
echo "AZURE_CLIENT_ID=${APP_ID}"
echo "AZURE_TENANT_ID=${TENANT_ID}"
echo "AZURE_SUBSCRIPTION_ID=${SUB_ID}"
