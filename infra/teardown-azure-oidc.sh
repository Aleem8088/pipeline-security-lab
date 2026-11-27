#!/usr/bin/env bash
# Removes everything setup-azure-oidc.sh created.
set -euo pipefail
export MSYS_NO_PATHCONV=1
APP="pipeline-security-lab-oidc"
APP_ID=$(az ad app list --display-name "$APP" --query "[0].appId" -o tsv)
if [ -n "$APP_ID" ]; then az ad app delete --id "$APP_ID"; fi
az group delete -n rg-pipeline-lab --yes --no-wait || true
echo "Teardown requested. Verify with: az group list; az ad app list --display-name $APP"
