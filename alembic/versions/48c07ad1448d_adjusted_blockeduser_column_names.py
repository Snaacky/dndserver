"""adjusted BlockedUser column names

Revision ID: 48c07ad1448d
Revises: 62baba80a478
Create Date: 2023-05-01 21:36:17.422612

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = "48c07ad1448d"
down_revision = "62baba80a478"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("blocked_users", sa.Column("blocked_by", sa.Integer(), nullable=True))
    op.add_column("blocked_users", sa.Column("account_id", sa.Integer(), nullable=True))
    op.add_column("blocked_users", sa.Column("character_id", sa.Integer(), nullable=True))
    op.add_column("blocked_users", sa.Column("nickname", sa.String(length=20), nullable=True))
    op.add_column("blocked_users", sa.Column("gender", sa.Enum("MALE", "FEMALE", name="gender"), nullable=True))
    op.add_column(
        "blocked_users",
        sa.Column(
            "character_class",
            sa.Enum(
                "BARBARIAN", "BARD", "CLERIC", "FIGHTER", "RANGER", "ROGUE", "WIZARD", "NONE", name="characterclass"
            ),
            nullable=True,
        ),
    )
    op.drop_column("blocked_users", "blocked_character_id")
    op.drop_column("blocked_users", "blockee_character_id")
    op.drop_column("blocked_users", "blocked_character_class")
    op.drop_column("blocked_users", "blocked_nickname")
    op.drop_column("blocked_users", "blocked_gender")
    op.drop_column("blocked_users", "blocked_account_id")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("blocked_users", sa.Column("blocked_account_id", sa.INTEGER(), nullable=True))
    op.add_column("blocked_users", sa.Column("blocked_gender", sa.VARCHAR(length=6), nullable=True))
    op.add_column("blocked_users", sa.Column("blocked_nickname", sa.VARCHAR(length=20), nullable=True))
    op.add_column("blocked_users", sa.Column("blocked_character_class", sa.VARCHAR(length=9), nullable=True))
    op.add_column("blocked_users", sa.Column("blockee_character_id", sa.INTEGER(), nullable=True))
    op.add_column("blocked_users", sa.Column("blocked_character_id", sa.INTEGER(), nullable=True))
    op.drop_column("blocked_users", "character_class")
    op.drop_column("blocked_users", "gender")
    op.drop_column("blocked_users", "nickname")
    op.drop_column("blocked_users", "character_id")
    op.drop_column("blocked_users", "account_id")
    op.drop_column("blocked_users", "blocked_by")
    # ### end Alembic commands ###