# Generic single-database configuration placeholders for Alembic scripts.

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_create_food_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create lookup tables first (no foreign keys to foods yet).
    op.create_table(
        "tags",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_tags_id"), "tags", ["id"], unique=False)

    op.create_table(
        "ingredients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_ingredients_id"), "ingredients", ["id"], unique=False)

    op.create_table(
        "dietary_types",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_dietary_types_id"), "dietary_types", ["id"], unique=False)

    op.create_table(
        "allergens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_allergens_id"), "allergens", ["id"], unique=False)

    # Main foods table
    op.create_table(
        "foods",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("food_category", sa.String(length=100), nullable=True),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column("preparation_time_minutes", sa.Integer(), nullable=True),
        sa.Column("serving_size", sa.String(length=50), nullable=True),
        sa.Column("serving_unit", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_foods_id"), "foods", ["id"], unique=False)

    # One-to-one nutrition table
    op.create_table(
        "food_nutrition",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("calories", sa.Float(), nullable=True),
        sa.Column("protein_g", sa.Float(), nullable=True),
        sa.Column("carbohydrates_g", sa.Float(), nullable=True),
        sa.Column("fat_g", sa.Float(), nullable=True),
        sa.Column("fibre_g", sa.Float(), nullable=True),
        sa.Column("sugar_g", sa.Float(), nullable=True),
        sa.Column("sodium_mg", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("food_id"),
    )
    op.create_index(op.f("ix_food_nutrition_id"), "food_nutrition", ["id"], unique=False)

    # Join tables
    op.create_table(
        "food_tags",
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"]),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"]),
        sa.PrimaryKeyConstraint("food_id", "tag_id"),
    )

    op.create_table(
        "food_ingredients",
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("ingredient_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.String(length=50), nullable=True),
        sa.Column("unit", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"]),
        sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"]),
        sa.PrimaryKeyConstraint("food_id", "ingredient_id"),
    )

    op.create_table(
        "food_dietary_types",
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("dietary_type_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["dietary_type_id"], ["dietary_types.id"]),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"]),
        sa.PrimaryKeyConstraint("food_id", "dietary_type_id"),
    )

    op.create_table(
        "food_allergens",
        sa.Column("food_id", sa.Integer(), nullable=False),
        sa.Column("allergen_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["allergen_id"], ["allergens.id"]),
        sa.ForeignKeyConstraint(["food_id"], ["foods.id"]),
        sa.PrimaryKeyConstraint("food_id", "allergen_id"),
    )


def downgrade() -> None:
    # Drop tables in reverse order (children first, then parents).
    op.drop_table("food_allergens")
    op.drop_table("food_dietary_types")
    op.drop_table("food_ingredients")
    op.drop_table("food_tags")
    op.drop_index(op.f("ix_food_nutrition_id"), table_name="food_nutrition")
    op.drop_table("food_nutrition")
    op.drop_index(op.f("ix_foods_id"), table_name="foods")
    op.drop_table("foods")
    op.drop_index(op.f("ix_allergens_id"), table_name="allergens")
    op.drop_table("allergens")
    op.drop_index(op.f("ix_dietary_types_id"), table_name="dietary_types")
    op.drop_table("dietary_types")
    op.drop_index(op.f("ix_ingredients_id"), table_name="ingredients")
    op.drop_table("ingredients")
    op.drop_index(op.f("ix_tags_id"), table_name="tags")
    op.drop_table("tags")
