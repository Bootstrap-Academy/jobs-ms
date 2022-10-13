"""add fields to jobs table

Revision ID: 66df982944f5
Create Date: 2022-10-13 18:34:21.175347
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "66df982944f5"
down_revision = "adf12906bb0c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs_jobs", sa.Column("_responsibilities", sa.Text(), nullable=True))
    op.add_column(
        "jobs_jobs",
        sa.Column(
            "professional_level",
            sa.Enum("ENTRY", "JUNIOR", "SENIOR", "MANAGER", name="professionallevel"),
            nullable=True,
        ),
    )
    op.add_column("jobs_jobs", sa.Column("salary_min", sa.BigInteger(), nullable=True))
    op.add_column("jobs_jobs", sa.Column("salary_max", sa.BigInteger(), nullable=True))
    op.add_column("jobs_jobs", sa.Column("salary_unit", sa.Text(), nullable=True))
    op.add_column(
        "jobs_jobs",
        sa.Column(
            "salary_per", sa.Enum("ONCE", "TASK", "HOUR", "DAY", "MONTH", "YEAR", name="salaryper"), nullable=True
        ),
    )
    op.add_column("jobs_jobs", sa.Column("last_update", sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs_jobs", "last_update")
    op.drop_column("jobs_jobs", "salary_per")
    op.drop_column("jobs_jobs", "salary_unit")
    op.drop_column("jobs_jobs", "salary_max")
    op.drop_column("jobs_jobs", "salary_min")
    op.drop_column("jobs_jobs", "professional_level")
    op.drop_column("jobs_jobs", "_responsibilities")
