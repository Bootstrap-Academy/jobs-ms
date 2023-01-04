"""Add level column to skill dependencies

Revision ID: b74604db38b3
Create Date: 2023-01-04 15:35:48.077721
"""

from alembic import op

import sqlalchemy as sa

from api import models


# revision identifiers, used by Alembic.
revision = "b74604db38b3"
down_revision = "adf12906bb0c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("jobs_skill_requirements", sa.Column("level", sa.Integer(), nullable=True))
    op.execute(sa.update(models.SkillRequirement).values(level=10))


def downgrade() -> None:
    op.drop_column("jobs_skill_requirements", "level")
