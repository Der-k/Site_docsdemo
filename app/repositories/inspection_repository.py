from app.repositories.base import Repository


class InspectionRepository(Repository):
    collection, prefix = "inspections", "INS-"


class InspectionTemplateRepository(Repository):
    collection, prefix = "inspection_templates", "T"
