import argparse
import logging
import os
import json
import sys
import shutil
import filecmp
from dataclasses import dataclass
from typing import List, Dict, Type, Callable
from UserInputHandler import UserInputHandler


class FileManager:

    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    file_handler: logging.FileHandler = logging.FileHandler('file_manager.log')
    stream_handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    log_formatter: logging.Formatter = logging.Formatter('%(asctime)s: %(name)s: %(levelname)s: %(message)s')
    file_handler.setFormatter(log_formatter)
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    @dataclass
    class Config:
        name: str
        type: Type

    default_file_attrs: Config = Config(name='default_file_attributes', type=str)
    unwanted_chars: Config = Config(name='unwanted_file_names_characters', type=list)
    substitute_char: Config = Config(name='unwanted_file_names_characters_substitute_char', type=str)
    tmp_file_extensions: Config = Config(name='file_extensions_considered_as_temporary', type=list)

    configuration_list: List[Config] = [default_file_attrs, unwanted_chars, substitute_char, tmp_file_extensions]

    def __init__(self):
        action_move_files_from_sources_to_target: str = 'm'
        action_remove_empty_files_from_target: str = 'e'
        action_remove_temp_files_from_target: str = 't'
        action_remove_duplicates_from_target: str = 'd'
        action_unify_file_permissions: str = 'p'
        action_change_bad_characters_in_file_names: str = 'c'
        actions_dict: Dict[str, Callable] = {
            action_move_files_from_sources_to_target: self.move_files_from_sources_to_target,
            action_remove_empty_files_from_target:


        }

        args = FileManager.get_args()
        self.target_dir: str = args.target[0]
        self.src_dirs: List[str] = args.source
        self.config_file_path: str = args.config[0]

        self.configurations = self.load_configurations()
        self.validate_configuration()

        self.validate_existence_of_dirs()

        # TODO
        self.is_all_global: bool = True

        self.is_global_move: bool = True
        self.keep_latest_file: bool = True

        self.is_global_remove_empty: bool = True
        self.is_global_remove_temp: bool = True

    @staticmethod
    def get_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='FileManager is a script that helps you in ordering and managing your files')
        parser.add_argument('-t', '--target', nargs=1, type=str, required=True, help='Target directory')
        parser.add_argument('-s', '--source', nargs='+', type=str, required=True,
                            help='Source directories (at least 1)')
        parser.add_argument('-c', '--config', nargs=1, type=str, required=True,
                            help='Path to configuration file (*.json)')
        # TODO
        parser.add_argument_group()
        return parser.parse_args()

    def load_configurations(self) -> Dict:
        try:
            with open(self.config_file_path, 'r') as f:
                data = json.load(f)
            return data
        except FileNotFoundError as e:
            FileManager.logger.error(e)
            exit(1)

    def validate_configuration(self) -> None:
        for config in FileManager.configuration_list:
            if config.name not in self.configurations:
                FileManager.logger.error(f'{config.name} is not present in configuration file')
                exit(1)
            elif type(self.configurations[config.name]) != config.type:
                FileManager.logger.error(f'{config.name} configuration must be of type {config.type}. '
                                         f'Got type {type(self.configurations[config.name])} instead')
                exit(1)

    def validate_existence_of_dirs(self) -> None:
        if not os.path.isdir(self.target_dir):
            FileManager.logger.error(f'Target directory {self.target_dir} does not exist')
            exit(1)
        for d in self.src_dirs:
            if not os.path.isdir(d):
                FileManager.logger.error(f'Source directory {d} does not exist')
                exit(1)

    def move_files_from_sources_to_target(self) -> None:
        self.is_global_move, self.keep_latest_file = UserInputHandler.ask_if_move_files_globally()
        for src_dir in self.src_dirs:
            self.move_files_from_directory_tree_to_target(src_dir)

    def move_files_from_directory_tree_to_target(self, directory) -> None:
        """
        Moves files from source directory to target directory.
        If directory has subdirectories, it calls itself recursively.
        """
        directory_elements: List[str] = os.listdir(directory)
        for dir_element in directory_elements:
            element_path: str = os.path.join(directory, dir_element)
            if os.path.isdir(element_path):
                self.move_files_from_directory_tree_to_target(element_path)
            elif os.path.isfile(element_path):
                self.move_file_to_target(element_path)
            else:
                print(f'Encountered unsupported directory element {element_path}\n'
                      f'Program supports only directories and files.')

    def move_file_to_target(self, file_path) -> None:
        if self.is_global_move or UserInputHandler.ask_if_move_file(file_path, self.target_dir):
            try:
                shutil.move(file_path, self.target_dir)
            except shutil.Error:  # File path conflict
                file_name: str = os.path.basename(file_path)
                target_file_path: str = os.path.join(self.target_dir, file_name)
                if self.is_global_move:
                    if self.keep_latest_file:
                        if os.path.getmtime(file_path) > os.path.getmtime(target_file_path):
                            os.remove(target_file_path)
                            shutil.move(file_path, target_file_path)
                    else:
                        if os.path.getmtime(file_path) < os.path.getmtime(target_file_path):
                            os.remove(target_file_path)
                            shutil.move(file_path, target_file_path)

    def remove_empty_files_from_target(self) -> None:
        self.is_global_remove_empty = UserInputHandler.ask_if_remove_empty_files_from_target_globally(self.target_dir)
        self.remove_empty_files_from_directory_tree(self.target_dir)

    def remove_empty_files_from_directory_tree(self, directory) -> None:
        pass

    def remove_empty_files_from_directory(self) -> None:
        pass

    def remove_temp_files_from_target(self) -> None:
        self.is_global_remove_temp = UserInputHandler.ask_if_remove_temp_files_from_target_globally(self.target_dir)
        self.remove_temp_files_from_directory_tree(self.target_dir)

    def remove_temp_files_from_directory_tree(self, directory) -> None:
        pass

    def remove_temp_files_from_directory(self) -> None:
        pass

    def remove_duplicates_from_target(self) -> None:
        pass

    def run(self) -> None:
        try:
            print(f'Moving files from source directories {" ,".join(self.src_dirs)} to target directory {self.target_dir}')
            self.move_files_from_sources_to_target()
            print(f'Removing empty files from target directory {self.target_dir} and its subdirectories')
            self.remove_empty_files_from_target()
            print(f'Removing temporary files from target directory {self.target_dir} and its subdirectories')
            self.remove_temp_files_from_target()
            print(f'Removing duplicated files from target directory {self.target_dir} and its subdirectories')
        except KeyboardInterrupt:
            print('Program closed')
            exit(0)
        except Exception as e:
            FileManager.logger.error(e)


def main() -> None:
    FileManager().run()


if __name__ == '__main__':
    main()
