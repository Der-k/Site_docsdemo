from app.repositories.base import Repository


class ActionRepository(Repository):
    collection, prefix = "actions", "ACT-"
