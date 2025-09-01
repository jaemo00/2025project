"""add updated_at to projects

Revision ID: 368433b0eb91
Revises: 
Create Date: 2025-08-20 20:53:56.218038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '368433b0eb91'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # SQLite에서는 server_default에 text를 사용하는 게 안전
    op.add_column(
        'projects',
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False)
    )
    # 기존 NULL 방지용 업데이트(필요시)
    # op.execute(sa.text("UPDATE projects SET updated_at = CURRENT_TIMESTAMP WHERE updated_at IS NULL"))

def downgrade():
    op.drop_column('projects', 'updated_at')