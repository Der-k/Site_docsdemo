from app.repositories.base import Repository


class InductionRepository(Repository):
    collection, prefix = "inductions", "I"


class InductionRecordRepository(Repository):
    collection, prefix = "induction_records", "R"
