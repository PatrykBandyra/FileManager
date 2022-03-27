import argparse
import os
import json
import filecmp
from typing import List, Dict


class FileManager:

    default_file_attrs: str = 'default_file_attributes'
    unwanted_chars: str = 'unwanted_file_names_characters'
    substitute_char: str = 'unwanted_file_names_characters_substitute_char'
    tmp_file_extensions: str = 'file_extensions_considered_as_temporary'

    def __init__(self):
        args = FileManager.get_args()
        self.target_dir: str = args.target[0]
        self.src_dirs: List[str] = args.source
        self.config_file_path: str = args.config[0]

        self.configurations = self.load_configurations()

        self.validate_existence_of_dirs()

    @staticmethod
    def get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='FileManager is a script that helps you in ordering and managing your files')
        parser.add_argument('-t', '--target', nargs=1, type=str, required=True, help='Target directory')
        parser.add_argument('-s', '--source', nargs='+', type=str, required=True,
                            help='Source directories (at least 1)')
        parser.add_argument('-c', '--config', nargs=1, type=str, required=True,
                            help='Path to configuration file (*.json)')
        return parser.parse_args()

    def load_configurations(self) -> Dict:
        try:
            with open(self.config_file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError as e:
            print(e)
            exit(1)

    def validate_configuration(self):
        pass

    def validate_existence_of_dirs(self):
        if not os.path.isdir(self.target_dir):
            print(f'Directory {self.target_dir} does not exist')
            exit(1)
        for d in self.src_dirs:
            if not os.path.isdir(d):
                print(f'Directory {d} does not exist')
                exit(1)

    def run(self):
        pass


def main():
    file_manager = FileManager()
    file_manager.run()


if __name__ == '__main__':
    main()
