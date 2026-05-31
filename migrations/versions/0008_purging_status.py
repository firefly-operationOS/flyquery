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

"""add PURGING status

Revision ID: 0008_purging_status
Revises: 0007_rls
"""
from alembic import op

revision = "0008_purging_status"
down_revision = "0007_rls"


def upgrade():
    op.execute("ALTER TABLE flyquery_workspaces DROP CONSTRAINT IF EXISTS ck_workspaces_status")
    op.execute(
        "ALTER TABLE flyquery_workspaces ADD CONSTRAINT ck_workspaces_status "
        "CHECK (status IN ('ACTIVE','ARCHIVED','PURGING'))"
    )


def downgrade():
    op.execute("ALTER TABLE flyquery_workspaces DROP CONSTRAINT IF EXISTS ck_workspaces_status")
