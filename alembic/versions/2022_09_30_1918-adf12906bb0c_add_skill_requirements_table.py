"""add skill_requirements table

Revision ID: adf12906bb0c
Create Date: 2022-09-30 19:18:05.575987
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "adf12906bb0c"
down_revision = "377d4bb5aa21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs_skill_requirements",
        sa.Column("job_id", sa.String(length=36), nullable=False),
        sa.Column("skill_id", sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(["job_id"], ["jobs_jobs.id"]),
        sa.PrimaryKeyConstraint("job_id", "skill_id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("jobs_skill_requirements")
