#!/usr/bin/env bash

IFS="," read -ra PORTS <<<"$WAIT_PORTS"
path=$(dirname "$0")

curl -o /dev/null -s -w "http://localhost:8080/manage/health: %{http_code}\n" http://localhost:8080/manage/health
curl -o /dev/null -s -w "http://localhost:8070/manage/health: %{http_code}\n" http://localhost:8070/manage/health
curl -o /dev/null -s -w "http://localhost:8060/manage/health: %{http_code}\n" http://localhost:8060/manage/health
curl -o /dev/null -s -w "http://localhost:8050/manage/health: %{http_code}\n" http://localhost:8050/manage/health

PIDs=()
for port in "${PORTS[@]}"; do
  "$path"/wait-for.sh -t 120 "http://localhost:$port/manage/health" -- echo "Host localhost:$port is active" &
  PIDs+=($!)
done

for pid in "${PIDs[@]}"; do
  if ! wait "${pid}"; then
    exit 1
  fi
done
