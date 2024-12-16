"""create_users_table

Revision ID: 950a5b28ed38
Revises: f17be03ff900
Create Date: 2024-12-16 14:00:47.831414

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "950a5b28ed38"
down_revision: Union[str, None] = "f17be03ff900"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
