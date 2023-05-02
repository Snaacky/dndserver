"""empty message

Revision ID: dd570a52541a
Revises: 555a5ce93305, 666ee8c39e0e
Create Date: 2023-05-02 02:25:51.254678

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = "dd570a52541a"
down_revision = ("555a5ce93305", "666ee8c39e0e")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
