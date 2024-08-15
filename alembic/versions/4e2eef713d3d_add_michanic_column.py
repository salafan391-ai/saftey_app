"""add michanic column

Revision ID: 4e2eef713d3d
Revises: 2ef0329af2c8
Create Date: 2024-08-07 14:58:18.396249

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4e2eef713d3d'
down_revision: Union[str, None] = '2ef0329af2c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('car_parts_detection',sa.Column('michanic',sa.String(),nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('car_parts_detection','michanic')
    pass
