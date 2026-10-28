"""Add salary and requirements to candidaturas.

Revision ID: 0002_salary_requirements
Revises: 0001_create_candidaturas
Create Date: 2026-10-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_salary_requirements"
down_revision: Union[str, None] = "0001_create_candidaturas"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("candidaturas", sa.Column("salario", sa.String(length=120), nullable=True))
    op.add_column("candidaturas", sa.Column("requisitos", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("candidaturas", "requisitos")
    op.drop_column("candidaturas", "salario")