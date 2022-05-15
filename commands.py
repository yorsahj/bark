import datetime as dt
import sys
import requests
from typing import Dict, Tuple
from abc import ABC, abstractmethod

from persistence import BookmarkDatabase

persistence = BookmarkDatabase()


class Command(ABC):
    @abstractmethod
    def execute(self, data):
        pass


class AddBookmarkCommand(Command):
    def execute(self, data, timestamp: str = None) -> Tuple:
        data['date_added'] = timestamp or dt.datetime.utcnow().isoformat()
        persistence.create(data)
        return True, None


class ListBookmarksCommand(Command):
    def __init__(self, order_by: str = 'date_added'):
        self.order_by = order_by

    def execute(self, data) -> Tuple:
        return True, persistence.list(order_by=self.order_by)


class DeleteBookmarkCommand(Command):
    def execute(self, data):
        persistence.delete(data)
        return True, None


class QuitCommand(Command):
    def execute(self, data):
        sys.exit()


class ImportGitHubStarsCommand(Command):
    @staticmethod
    def _extract_bookmark_info(repo: Dict) -> Dict:
        return {
            'title': repo['name'],
            'url': repo['html_url'],
            'notes': repo['description'],
        }

    def execute(self, data: Dict):
        bookmarks_imported = 0
        github_username = data['github_username']
        next_page_of_results = f'https://api.github.com/users/{github_username}/starred'
        while next_page_of_results:
            stars_response = requests.get(
                next_page_of_results,
                headers={'Accept': 'application/vnd.github.v3.star+json'},
            )
            next_page_of_results = stars_response.links.get('next', {}).get('url')
            for repo_info in stars_response.json():
                repo = repo_info['repo']
                if data['preserve_timestamps']:
                    timestamp = dt.datetime.strptime(repo_info['starred_at'], '%Y-%m-%dT%H:%M:%SZ')
                else:
                    timestamp = None

                bookmarks_imported += 1
                AddBookmarkCommand().execute(self._extract_bookmark_info(repo), timestamp=timestamp)

        return f'Imported {bookmarks_imported} bookmarks from the starred repo!'
