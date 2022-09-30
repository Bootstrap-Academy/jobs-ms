"""add companies table

Revision ID: e920566013c8
Create Date: 2022-09-30 16:57:11.741223
"""

from alembic import op

import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e920566013c8"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "jobs_companies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("youtube_video", sa.String(length=255), nullable=True),
        sa.Column("twitter_handle", sa.String(length=255), nullable=True),
        sa.Column("instagram_handle", sa.String(length=255), nullable=True),
        sa.Column("logo_url", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("id"),
        sa.UniqueConstraint("name"),
        mysql_collate="utf8mb4_bin",
    )


def downgrade() -> None:
    op.drop_table("jobs_companies")
