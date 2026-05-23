# Copyright 2026 Firefly Software Solutions Inc
"""Allow UNKNOWN ast_classification on flyquery_queries.

The previous check constraint rejected UNKNOWN with a CheckViolationError,
which surfaced as a 500 on the query endpoint for SQL the AST classifier
couldn't categorise (set operations, CTEs that the classifier didn't
recognise as SELECT-shape, etc).

The classifier is now stricter -- UNION/INTERSECT/EXCEPT are classified
as SELECT -- but the database still needs to accept UNKNOWN as a
legitimate fallback so a future classifier gap doesn't 500.

Revision: 0010_allow_unknown_ast
Down revision: 0009_relations_unique_constraint
"""

from __future__ import annotations

from alembic import op

revision = "0010_allow_unknown_ast"
down_revision = "0009_relations_unique_constraint"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("ck_queries_ast", "flyquery_queries", type_="check")
    op.create_check_constraint(
        "ck_queries_ast",
        "flyquery_queries",
        "ast_classification IS NULL OR "
        "ast_classification IN ('SELECT','INSERT','UPDATE','DELETE','DDL','UNKNOWN')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_queries_ast", "flyquery_queries", type_="check")
    op.create_check_constraint(
        "ck_queries_ast",
        "flyquery_queries",
        "ast_classification IS NULL OR "
        "ast_classification IN ('SELECT','INSERT','UPDATE','DELETE','DDL')",
    )
