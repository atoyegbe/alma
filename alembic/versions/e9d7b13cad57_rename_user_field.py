"""rename user field

Revision ID: e9d7b13cad57
Revises: 0005f6c627bb
Create Date: 2024-03-03 01:14:34.606638

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e9d7b13cad57'
down_revision: Union[str, None] = '0005f6c627bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
