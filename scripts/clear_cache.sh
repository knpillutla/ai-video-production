#!/usr/bin/env bash
# ==============================================================================
# Clear AI Video Producer Studio caches, topic deduplication vault, and test renders.
# Usage:
#   ./scripts/clear_cache.sh
#   ./scripts/clear_cache.sh --user-id user_krishna_01
# ==============================================================================

set -eo pipefail

USER_ID=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --user-id|-u)
      USER_ID="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Usage: ./scripts/clear_cache.sh [--user-id <user_id>]"
      exit 1
      ;;
  esac
done

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
STORAGE_DIR="$PROJECT_ROOT/storage"
VAULT_FILE="$STORAGE_DIR/topic_memory_vault.json"
DB_FILE="$STORAGE_DIR/db_state.json"

echo -e "\033[0;36m========================================================================\033[0m"
echo -e "\033[0;36m             CLEARING STUDIO CACHES & DEDUPLICATION TOPICS             \033[0m"
echo -e "\033[0;36m========================================================================\033[0m"

# 1. Clear Topic Memory Vault (Deduplication topics)
echo -e "\n\033[0;33m[*] Clearing Topic Memory Deduplication Vault...\033[0m"
if [ -f "$VAULT_FILE" ]; then
  if [ -n "$USER_ID" ]; then
    python3 -c "
import json, sys
vault_path = '$VAULT_FILE'
user_id = '$USER_ID'
try:
    with open(vault_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    initial_len = len(data)
    filtered = [e for e in data if str(e.get('user_id', '')) != user_id and str(e.get('user_id', '')) != f'user-{user_id}']
    with open(vault_path, 'w', encoding='utf-8') as f:
        json.dump(filtered, f, indent=2)
    print(f'    -> Cleared {initial_len - len(filtered)} deduplication topic(s) for user {user_id}.')
except Exception as exc:
    print(f'    -> Vault filtering error: {exc}')
" 2>/dev/null || true
  else
    echo "[]" > "$VAULT_FILE"
    echo -e "\033[0;32m    -> Reset storage/topic_memory_vault.json to empty list [].\033[0m"
  fi
else
  mkdir -p "$STORAGE_DIR"
  echo "[]" > "$VAULT_FILE"
  echo -e "\033[0;32m    -> Initialized fresh storage/topic_memory_vault.json.\033[0m"
fi

# 2. Clear Rendered Episodes & Storage Caches
echo -e "\n\033[0;33m[*] Clearing Rendered Episodes and Storage Caches...\033[0m"
if [ -n "$USER_ID" ]; then
  CLEAN_USER=$(echo "$USER_ID" | tr '_' '-' | tr '[:upper:]' '[:lower:]')
  find "$STORAGE_DIR" -maxdepth 1 -type d -name "*$CLEAN_USER*" -exec rm -rf {} + 2>/dev/null || true
  echo -e "\033[0;32m    -> Cleared storage directories for user '$USER_ID'.\033[0m"
else
  find "$STORAGE_DIR" -maxdepth 1 -type d -name "user-*" -exec rm -rf {} + 2>/dev/null || true
  echo -e "\033[0;32m    -> Removed user render storage folders.\033[0m"
fi

# 3. Clear DB State (Projects / Episodes / Shows)
if [ -z "$USER_ID" ]; then
  echo -e "\n\033[0;33m[*] Resetting Database State (storage/db_state.json)...\033[0m"
  if [ -f "$DB_FILE" ]; then
    rm -f "$DB_FILE"
    echo -e "\033[0;32m    -> Cleared storage/db_state.json for fresh testing.\033[0m"
  fi
fi

# 4. Clear Python __pycache__ and bytecode
echo -e "\n\033[0;33m[*] Clearing Python bytecode caches (__pycache__, *.pyc)...\033[0m"
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
echo -e "\033[0;32m    -> Cleaned all __pycache__ directories and .pyc files.\033[0m"

# 5. Clear Pytest Cache
echo -e "\n\033[0;33m[*] Clearing Pytest Cache (.pytest_cache)...\033[0m"
rm -rf "$PROJECT_ROOT/.pytest_cache" 2>/dev/null || true
echo -e "\033[0;32m    -> Cleared .pytest_cache.\033[0m"

# 6. Clear Temporary Scratch Files
SCRATCH_DIR="$PROJECT_ROOT/scratch"
if [ -d "$SCRATCH_DIR" ]; then
  find "$SCRATCH_DIR" -type f -name "test_*" -delete 2>/dev/null || true
  echo -e "\033[0;32m    -> Cleaned temporary scratch test files.\033[0m"
fi

echo -e "\n\033[0;36m========================================================================\033[0m"
echo -e "\033[0;32m               ALL CACHES & TOPIC MEMORY CLEARED!                       \033[0m"
echo -e "\033[0;36m========================================================================\033[0m"
echo -e "Ready for fresh automated testing and interactive video synthesis.\n"
