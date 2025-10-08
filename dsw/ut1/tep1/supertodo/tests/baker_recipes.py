from faker import Faker
from model_bakery.recipe import Recipe

fake = Faker()


task = Recipe(
    'tasks.Task',
    name=fake.sentence,
    slug=fake.slug,
    description=fake.text,
    completed=fake.boolean,
)
