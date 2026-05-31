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

"""Add unique constraint on flyquery_relations for UPSERT support.

Revision ID: 0009_relations_unique_constraint
Revises: 0008_purging_status
"""

from alembic import op

revision = "0009_relations_unique_constraint"
down_revision = "0008_purging_status"


def upgrade():
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_relations_pair
        ON flyquery_relations (from_table_id, from_column_name, to_table_id, to_column_name)
        """
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_relations_pair")
