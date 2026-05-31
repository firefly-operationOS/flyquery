#!/usr/bin/env sh
# Copyright 2024-2026 Firefly Software Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#
# Dispatcher for the flyquery container.
#
#   ./docker-entrypoint.sh serve    -- run the FastAPI server (default)
#   ./docker-entrypoint.sh worker   -- run the EDA worker
#   ./docker-entrypoint.sh migrate  -- run alembic upgrade head and exit
#
# When RUN_MIGRATIONS=true, migrate-then-serve is invoked.
set -eu

if [ "${RUN_MIGRATIONS:-false}" = "true" ]; then
  echo "[entrypoint] RUN_MIGRATIONS=true -- running migrations first"
  alembic upgrade head
fi

cmd="${1:-serve}"
shift || true

case "${cmd}" in
  serve)
    exec flyquery serve "$@"
    ;;
  worker)
    exec flyquery worker "$@"
    ;;
  migrate)
    exec alembic upgrade head
    ;;
  *)
    # Allow ad-hoc commands (sh, alembic <foo>, etc.)
    exec "${cmd}" "$@"
    ;;
esac
