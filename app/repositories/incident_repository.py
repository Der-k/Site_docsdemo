from app.repositories.base import Repository


class IncidentRepository(Repository):
    collection, prefix = "incidents", "INC-"
