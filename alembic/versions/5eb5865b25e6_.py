"""empty message

Revision ID: 5eb5865b25e6
Revises: 62baba80a478, 666ee8c39e0e
Create Date: 2023-05-04 03:40:40.746398

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = "5eb5865b25e6"
down_revision = ("62baba80a478", "666ee8c39e0e")
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
