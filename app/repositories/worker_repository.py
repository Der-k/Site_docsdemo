from app.repositories.base import Repository


class WorkerRepository(Repository):
    collection, prefix = "workers", "W"


class CertificationRepository(Repository):
    collection, prefix = "certifications", "C"

    def for_worker(self, worker_id):
        return [c for c in self.all() if c["worker_id"] == worker_id]
