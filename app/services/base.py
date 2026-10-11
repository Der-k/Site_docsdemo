from app.data import storage


class Repository:
    collection = ""
    prefix = ""

    def all(self):
        return storage.list_records(self.collection)

    def get(self, record_id):
        return storage.get_record(self.collection, record_id)

    def add(self, record):
        return storage.add_record(self.collection, record, self.prefix)

    def update(self, record_id, **changes):
        return storage.update_record(self.collection, record_id, changes)
