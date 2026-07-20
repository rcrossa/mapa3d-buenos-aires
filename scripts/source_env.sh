#!/usr/bin/env bash
# source_env.sh — Shared .env parsing for DOWNLOAD_URL and DOWNLOAD_TOKEN.
# Usage: source scripts/source_env.sh
if [ -f .env ]; then
    while IFS='=' read -r key value; do
        key="${key#[[:space:]]}"; key="${key%[[:space:]]}"
        value="${value# }"
        case "$key" in
            ''|\#*) continue ;;
            DOWNLOAD_URL)     DOWNLOAD_URL="$value" ;;
            DOWNLOAD_TOKEN)   DOWNLOAD_TOKEN="$value" ;;
        esac
    done < .env
fi
