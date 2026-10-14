#!/usr/bin/env bash
# Create the shared triage labels in every public Querya repository.
# Existing labels with the same name are updated, others are left untouched.
# Usage: scripts/sync_labels.sh [repo ...]   (default: all public repos of the org)
set -euo pipefail
ORG=QueryaHub
LABELS=(
  "needs-triage|fbca04|Awaiting maintainer review"
  "needs-info|d4c5f9|Waiting for more information from the reporter"
  "stale|ededed|No recent activity"
  "security|b60205|Security related"
  "blocked|000000|Blocked by another issue or an external factor"
)
repos=("$@")
if [ ${#repos[@]} -eq 0 ]; then
  mapfile -t repos < <(gh repo list "$ORG" --visibility public --no-archived --source --json name --jq '.[].name' | grep -v '^\.github$')
fi
for repo in "${repos[@]}"; do
  for l in "${LABELS[@]}"; do
    IFS='|' read -r name color desc <<<"$l"
    gh label create "$name" --repo "$ORG/$repo" --color "$color" --description "$desc" --force >/dev/null
  done
  echo "labels synced: $repo"
done
