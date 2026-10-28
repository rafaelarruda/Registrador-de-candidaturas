"""Create the initial candidaturas table.

Revision ID: 0001_create_candidaturas
Revises:
Create Date: 2026-10-28
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_candidaturas"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    if sa.inspect(op.get_bind()).has_table("candidaturas"):
        return

    op.create_table(
        "candidaturas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("empresa", sa.String(length=150), nullable=False),
        sa.Column("cargo", sa.String(length=150), nullable=False),
        sa.Column("link", sa.String(length=2048), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "enviado",
                "entrevista",
                "oferta",
                "recusado",
                name="applicationstatus",
                native_enum=False,
                length=20,
            ),
            nullable=False,
        ),
        sa.Column("anotacoes", sa.Text(), nullable=True),
        sa.Column(
            "data_candidatura",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_candidaturas_id", "candidaturas", ["id"], unique=False)
    op.create_index("ix_candidaturas_empresa", "candidaturas", ["empresa"], unique=False)
    op.create_index("ix_candidaturas_cargo", "candidaturas", ["cargo"], unique=False)
    op.create_index("ix_candidaturas_status", "candidaturas", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_candidaturas_status", table_name="candidaturas")
    op.drop_index("ix_candidaturas_cargo", table_name="candidaturas")
    op.drop_index("ix_candidaturas_empresa", table_name="candidaturas")
    op.drop_index("ix_candidaturas_id", table_name="candidaturas")
    op.drop_table("candidaturas")