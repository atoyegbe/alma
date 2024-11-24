"""rename user field

Revision ID: 4d8bf4355150
Revises: e9d7b13cad57
Create Date: 2024-03-03 01:20:35.206691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d8bf4355150'
down_revision: Union[str, None] = 'e9d7b13cad57'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
