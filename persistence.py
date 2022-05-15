from abc import ABC, abstractmethod
from database import DatabaseManager


class PersistenceLayer(ABC):
    @abstractmethod
    def create(self, data):
        raise NotImplementedError('persistence layers must implement this method')

    @abstractmethod
    def list(self, order_by=None):
        raise NotImplementedError('persistence layers must implement this method')

    @abstractmethod
    def delete(self, bookmark_id):
        raise NotImplementedError('persistence layers must implement this method')


class BookmarkDatabase(PersistenceLayer):
    def __init__(self):
        self.table_name = 'bookmarks'
        self.db = DatabaseManager('bookmarks.db')
        self.db.create_table(self.table_name, {
            'id': 'integer primary key autoincrement',
            'title': 'text not null',
            'url': 'text not null',
            'notes': 'text',
            'date_added': 'text not null',
        })

    def create(self, bookmark_data):
        self.db.add(self.table_name, bookmark_data)

    def list(self, order_by=None):
        return self.db.select(self.table_name, order_by=order_by).fetchall()

    def delete(self, bookmark_id):
        self.db.delete(self.table_name, {'id': bookmark_id})
