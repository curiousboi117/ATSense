"""create initial schema

Revision ID: f40d59efac2c
Revises:
Create Date: 2026-09-08

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f40d59efac2c"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create the initial database schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index(
        op.f("ix_users_id"),
        "users",
        ["id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_users_username"),
        "users",
        ["username"],
        unique=False,
    )

    op.create_table(
        "job_descriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_job_descriptions_id"),
        "job_descriptions",
        ["id"],
        unique=False,
    )

    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_resumes_id"),
        "resumes",
        ["id"],
        unique=False,
    )

    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=True),
        sa.Column("job_description_id", sa.Integer(), nullable=True),
        sa.Column("ats_score", sa.Float(), nullable=False),
        sa.Column("score_breakdown", sa.JSON(), nullable=False),
        sa.Column("personal_info", sa.JSON(), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=False),
        sa.Column("ats_checks", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("similarity_metrics", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["job_description_id"],
            ["job_descriptions.id"],
        ),
        sa.ForeignKeyConstraint(
            ["resume_id"],
            ["resumes.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_analyses_id"),
        "analyses",
        ["id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop the initial database schema."""
    op.drop_index(op.f("ix_analyses_id"), table_name="analyses")
    op.drop_table("analyses")

    op.drop_index(
        op.f("ix_resumes_id"),
        table_name="resumes",
    )
    op.drop_table("resumes")

    op.drop_index(
        op.f("ix_job_descriptions_id"),
        table_name="job_descriptions",
    )
    op.drop_table("job_descriptions")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_table("users")