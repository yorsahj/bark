import os
from collections import OrderedDict
from typing import Dict

import commands


def format_bookmark(bookmark):
    return '\t'.join(
        str(field) if field else ''
        for field in bookmark
    )


class Option:
    def __init__(self, name: str, command: commands.Command, prep_call=None, success_message='{result}'):
        self.name = name
        self.command = command
        self.prep_call = prep_call
        self.success_message = success_message

    def choose(self) -> None:
        data = self.prep_call() if self.prep_call else None
        success, result = self.command.execute(data)

        formatted_result = ''

        if isinstance(result, list):
            for bookmark in result:
                formatted_result += '\n' + format_bookmark(bookmark)
        else:
            formatted_result = result

        if success:
            print(self.success_message.format(result=formatted_result))

    def __str__(self) -> str:
        return self.name


def clear_screen():
    clear = 'cls' if os.name == 'nt' else 'clear'
    os.system(clear)


def print_options(options: Dict):
    for shortcut, option in options.items():
        print(f'({shortcut} {option}')
    print()


def option_choice_is_valid(choice: str, options: Dict) -> bool:
    return choice in options or choice.upper() in options


def get_option_choice(options: Dict):
    choice = input('Choose an action: ')
    while not option_choice_is_valid(choice, options):
        print('Unacceptable option')
        choice = input('Choose an action: ')
    return options[choice.upper()]


def get_user_input(label: str, required: bool = True) -> str:
    value = input(f'{label}: ') or None
    while required and not value:
        value = input(f'{label}: ') or None
    return value


def get_new_bookmark_data():
    return {
        'title': get_user_input('Title'),
        'url': get_user_input('URL'),
        'notes': get_user_input('Notes', required=False),
    }


def get_bookmark_id_for_deletion() -> str:
    return get_user_input('Enter a bookmark ID to delete')


def get_github_import_options():
    return {'github_username': get_user_input('GitHub user name'),
            'preserve_timestamps': get_user_input('Save timestamps? [Y/y]', required=False) in {'Y', 'y', None},
            }


def loop():
    c_options = OrderedDict({
        'A': Option('Add a bookmark',
                    commands.AddBookmarkCommand(),
                    prep_call=get_new_bookmark_data,
                    success_message='Bookmark added!'),
        'B': Option('List all bookmarks sorted by date',
                    commands.ListBookmarksCommand()),
        'T': Option('List all bookmarks sorted by title',
                    commands.ListBookmarksCommand(order_by='title')),
        'D': Option('Delete a bookmark',
                    commands.DeleteBookmarkCommand(),
                    prep_call=get_bookmark_id_for_deletion,
                    success_message='Bookmark deleted!'),
        'G': Option('Import GitHub stars',
                    commands.ImportGitHubStarsCommand(),
                    prep_call=get_github_import_options,
                    success_message='Imported {result} bookmarks!'),
        'Q': Option('Quit',
                    commands.QuitCommand()),
    })
    clear_screen()
    print_options(c_options)
    chosen_option = get_option_choice(c_options)
    clear_screen()
    chosen_option.choose()
    _ = input('Press ENTER to return to the menu')


if __name__ == '__main__':
    while True:
        loop()
