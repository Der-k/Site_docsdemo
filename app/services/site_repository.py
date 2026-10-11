from app.repositories.base import Repository


class SiteRepository(Repository):
    collection, prefix = "sites", "S"
