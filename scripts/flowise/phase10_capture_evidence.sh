#!/usr/bin/env bash
set -euo pipefail

GRAPH_ID="${1:-c45d7111-43d9-4ffa-a888-5f1ca1ade781}"
SESSION_ID="${2:-}"
DB_PATH="${FLOWISE_DB_PATH:-/root/.flowise/database.sqlite}"

if [ -z "${GRAPH_ID}" ]; then
  echo "ERROR: graph id is required" >&2
  exit 2
fi

if [ -n "${SESSION_ID}" ]; then
  EXECUTION_WHERE="sessionId='${SESSION_ID}'"
else
  EXECUTION_WHERE="agentflowId='${GRAPH_ID}'"
fi

echo "=== PHASE 10 FLOWISE EVIDENCE CAPTURE ==="
echo "GRAPH_ID=${GRAPH_ID}"
if [ -n "${SESSION_ID}" ]; then
  echo "SESSION_ID=${SESSION_ID}"
else
  echo "SESSION_ID=latest_for_graph"
fi

echo "=== GRAPH METADATA ==="
sqlite3 "${DB_PATH}" "SELECT id,name,type,deployed,isPublic,length(flowData),createdDate,updatedDate FROM chat_flow WHERE id='${GRAPH_ID}';"

echo "=== GRAPH_FLOWDATA_SHA256 ==="
sqlite3 "${DB_PATH}" "SELECT flowData FROM chat_flow WHERE id='${GRAPH_ID}';" | sha256sum | awk '{print $1}'

echo "=== EXECUTION METADATA ==="
sqlite3 "${DB_PATH}" "SELECT id,state,agentflowId,sessionId,length(executionData),createdDate,updatedDate FROM execution WHERE ${EXECUTION_WHERE} ORDER BY createdDate DESC LIMIT 5;"

LATEST_EXECUTION_ID="$(sqlite3 "${DB_PATH}" "SELECT id FROM execution WHERE ${EXECUTION_WHERE} ORDER BY createdDate DESC LIMIT 1;")"

if [ -z "${LATEST_EXECUTION_ID}" ]; then
  echo "ERROR: no execution found" >&2
  exit 3
fi

echo "=== LATEST_EXECUTION_ID ==="
echo "${LATEST_EXECUTION_ID}"

echo "=== EXECUTIONDATA_SHA256 ==="
sqlite3 "${DB_PATH}" "SELECT executionData FROM execution WHERE id='${LATEST_EXECUTION_ID}';" | sha256sum | awk '{print $1}'
