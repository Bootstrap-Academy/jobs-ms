"""add jobs table

Revision ID: 377d4bb5aa21
Create Date: 2022-09-30 18:49:47.416523
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "377d4bb5aa21"
down_revision = "e920566013c8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs_jobs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("company_id", sa.String(length=36), nullable=True),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("remote", sa.Boolean(), nullable=True),
        sa.Column(
            "type",
            sa.Enum("FULL_TIME", "PART_TIME", "INTERNSHIP", "TEMPORARY", "MINI_JOB", name="jobtype"),
            nullable=True,
        ),
        sa.Column("contact", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["company_id"], ["jobs_companies.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("jobs_jobs")
