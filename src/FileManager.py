import argparse
import logging
import os
import json
import sys
import shutil
import hashlib
from dataclasses import dataclass
from collections import defaultdict
from typing import List, Dict, Type, Callable, BinaryIO, DefaultDict, Tuple
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

    default_file_permissions: Config = Config(name='default_file_permissions', type=str)
    unusual_file_permissions: Config = Config(name='unusual_file_permissions', type=list)
    unwanted_chars: Config = Config(name='unwanted_file_names_characters', type=list)
    substitute_char: Config = Config(name='unwanted_file_names_characters_substitute_char', type=str)
    tmp_file_extensions: Config = Config(name='file_extensions_considered_as_temporary', type=list)

    configuration_list: List[Config] = [default_file_permissions, unusual_file_permissions, unwanted_chars,
                                        substitute_char, tmp_file_extensions]

    def __init__(self):
        action_move_files_from_sources_to_target: str = 'm'
        action_remove_empty_files_from_target: str = 'e'
        action_remove_temp_files_from_target: str = 't'
        action_remove_duplicates_from_target: str = 'd'
        action_unify_file_permissions: str = 'p'
        action_change_bad_characters_in_file_names: str = 'c'
        action_run_all: str = 'a'
        self.actions_dict: Dict[str, Callable] = {
            action_move_files_from_sources_to_target: self.move_files_from_sources_to_target,
            action_remove_empty_files_from_target: self.remove_empty_files_from_target,
            action_remove_temp_files_from_target: self.remove_temp_files_from_target,
            action_remove_duplicates_from_target: self.remove_duplicates_from_target,
            action_unify_file_permissions: self.unify_files_permissions,
            action_change_bad_characters_in_file_names: self.replace_bad_chars_in_file_names,
            action_run_all: self.run
        }

        args = self.get_args()
        self.target_dir: str = args.target[0]
        self.src_dirs: List[str] = args.source
        self.config_file_path: str = args.config[0]
        self.action: str = args.action[0]

        if self.src_dirs is None and self.action in [action_move_files_from_sources_to_target, action_run_all]:
            print('This action requires to pass source directories as arguments')
            exit(1)

        self.configurations = self.load_configurations()
        self.validate_configuration()

        self.validate_existence_of_dirs()

        self.is_global_move: bool = True
        self.keep_latest_file: bool = True

        self.is_global_remove_empty: bool = True
        self.is_global_remove_temp: bool = True

        self.is_global_remove_dupl: bool = True
        self.is_sort_by_ctime: bool = True

        self.is_global_file_permissions_unification: bool = True

        self.is_global_file_names_change: bool = True
        self.is_global_override_files: bool = True

        self.actions_dict[self.action]()  # Run method based on action chosen by user

    def get_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            description='FileManager is a script that helps you in ordering and managing your files')
        parser.add_argument('-t', '--target', nargs=1, type=str, required=True, help='Target directory')
        parser.add_argument('-s', '--source', nargs='+', type=str, required=False,
                            help='Source directories (at least 1)')
        parser.add_argument('-c', '--config', nargs=1, type=str, required=True,
                            help='Path to configuration file (*.json)')
        parser.add_argument('-a', '--action', nargs=1, type=str, required=True, choices=[*self.actions_dict.keys()],
                            help='Action to be performed on target directory')
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
        if self.src_dirs is not None:
            for d in self.src_dirs:
                if not os.path.isdir(d):
                    FileManager.logger.error(f'Source directory {d} does not exist')
                    exit(1)

    def move_files_from_sources_to_target(self) -> None:
        self.is_global_move, self.keep_latest_file = UserInputHandler.ask_if_move_files_globally()
        for src_dir in self.src_dirs:
            self.move_files_from_directory_tree_to_target(src_dir)

    def move_files_from_directory_tree_to_target(self, directory: str) -> None:
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
                FileManager.logger.info(f'Encountered unsupported directory element {element_path}. '
                                        f'Program supports only directories and files.')

    def move_file_to_target(self, file_path: str) -> None:
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
                else:
                    if UserInputHandler.ask_if_keep_latest_file(target_file_path):
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

    def remove_empty_files_from_directory_tree(self, directory: str) -> None:
        """
        Removes empty files from given directory.
        If directory has subdirectories, it calls itself recursively.
        """
        directory_elements: List[str] = os.listdir(directory)
        for dir_element in directory_elements:
            element_path: str = os.path.join(directory, dir_element)
            if os.path.isdir(element_path):
                self.remove_empty_files_from_directory_tree(element_path)
            elif os.path.isfile(element_path):
                self.remove_empty_files_from_directory(element_path)
            else:
                FileManager.logger.info(f'Encountered unsupported directory element {element_path}. '
                                        f'Program supports only directories and files.')

    def remove_empty_files_from_directory(self, file_path: str) -> None:
        if os.path.getsize(file_path) == 0:
            if self.is_global_remove_empty or UserInputHandler.ask_if_remove_empty_file(file_path):
                try:
                    os.remove(file_path)
                except Exception as e:
                    FileManager.logger.error(f'Could not remove {file_path}. '
                                             f'ERROR: {e}')

    def remove_temp_files_from_target(self) -> None:
        self.is_global_remove_temp = UserInputHandler.ask_if_remove_temp_files_from_target_globally(self.target_dir)
        self.remove_temp_files_from_directory_tree(self.target_dir)

    def remove_temp_files_from_directory_tree(self, directory: str) -> None:
        """
        Removes temporary files from given directory.
        If directory has subdirectories, it calls itself recursively.
        """
        directory_elements: List[str] = os.listdir(directory)
        for dir_element in directory_elements:
            element_path: str = os.path.join(directory, dir_element)
            if os.path.isdir(element_path):
                self.remove_temp_files_from_directory_tree(element_path)
            elif os.path.isfile(element_path):
                self.remove_temp_files_from_directory(element_path)
            else:
                FileManager.logger.info(f'Encountered unsupported directory element {element_path}. '
                                        f'Program supports only directories and files.')

    def remove_temp_files_from_directory(self, file_path: str) -> None:
        for extension in self.configurations[FileManager.tmp_file_extensions.name]:
            if file_path.endswith(extension):
                if self.is_global_remove_temp or UserInputHandler.ask_if_remove_temp_file(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        FileManager.logger.error(f'Could not remove {file_path}. '
                                                 f'ERROR: {e}')

    def remove_duplicates_from_target(self) -> None:
        self.is_global_remove_dupl = UserInputHandler.ask_if_remove_dupl_files_from_target_globally(self.target_dir)
        self.is_sort_by_ctime = UserInputHandler.ask_if_sort_dupl_files_by_ctime()
        self.remove_dupl_files_from_directory_tree(self.target_dir)

    def remove_dupl_files_from_directory_tree(self, directory: str) -> None:
        """
        Removes duplicated files from directory tree by creating hashes from files and its sizes.
        """

        def get_hash(file_full_path: str, first_chunk_only: bool = False, hash_algo: Callable = hashlib.sha1):
            """Generates hash from file"""

            def chunk_reader(file_obj: BinaryIO, chunk_size: int = 1024):
                """Generator that reads a file in chunks of bytes"""
                while True:
                    chunk = file_obj.read(chunk_size)
                    if not chunk:
                        return
                    yield chunk

            hash_obj = hash_algo()
            with open(file_full_path, 'rb') as file:
                if first_chunk_only:
                    hash_obj.update(file.read(1024))
                else:
                    for file_chunk in chunk_reader(file):
                        hash_obj.update(file_chunk)
            return hash_obj.digest()

        def sort_files_by_modification_date(file_full_path: str):
            return os.path.getmtime(file_full_path)

        def sort_files_by_creation_date(file_full_path: str):
            return os.path.getctime(file_full_path)

        files_by_size: DefaultDict[int, list] = defaultdict(list)
        files_by_small_hash: DefaultDict[Tuple, list] = defaultdict(list)
        files_by_full_hash: DefaultDict = defaultdict(list)

        for dir_path, _, file_names in os.walk(directory):
            for file_name in file_names:
                file_path: str = os.path.join(dir_path, file_name)
                try:
                    full_path: str = os.path.realpath(file_path)  # Dereferencing symlink
                    file_size: int = os.path.getsize(full_path)
                except OSError as e:
                    FileManager.logger.error(f'Could not access {file_path}. {e}')
                    continue
                files_by_size[file_size].append(full_path)

        # For all files with the same file size, get their hash on the first 1024 bytes
        for file_size, files in files_by_size.items():
            if len(files) < 2:
                continue  # This file size is unique

            for file_path in files:
                try:
                    small_hash = get_hash(file_path, first_chunk_only=True)
                except OSError as e:
                    FileManager.logger.error(f'Could not access {file_path}. '
                                             f'File permissions might have changed during program execution. {e}')
                    continue
                files_by_small_hash[(file_size, small_hash)].append(file_path)

        #  For all files with the same hash on the first 1024 bytes, get their hash on the full file
        for files in files_by_small_hash.values():
            if len(files) < 2:
                continue  # Small hash is unique

            for file_path in files:
                try:
                    full_hash = get_hash(file_path, first_chunk_only=False)
                except OSError as e:
                    FileManager.logger.error(f'Could not access {file_path}. '
                                             f'File permissions might have changed during program execution. {e}')
                    continue
                files_by_full_hash[full_hash].append(file_path)

        # Go over duplicates and leave the oldest one
        for files in files_by_full_hash.values():
            # Sort duplicates
            if self.is_sort_by_ctime:
                files.sort(key=sort_files_by_creation_date)
            else:
                files.sort(key=sort_files_by_modification_date)

            for file_path in files[1:]:  # Removing duplicated files; the oldest file is left
                if self.is_global_remove_dupl or UserInputHandler.ask_if_remove_dupl_file(file_path):
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        FileManager.logger.error(f'Could not remove {file_path}\n'
                                                 f'ERROR: {e}')

    def unify_files_permissions(self) -> None:
        self.is_global_file_permissions_unification = \
            UserInputHandler.ask_if_unify_files_perm_globally(self.target_dir,
                                                              self.configurations[FileManager.default_file_permissions],
                                                              self.configurations[FileManager.unusual_file_permissions])
        self.unify_files_permissions_in_directory_tree(self.target_dir)

    def unify_files_permissions_in_directory_tree(self, directory: str) -> None:
        directory_elements: List[str] = os.listdir(directory)
        for dir_element in directory_elements:
            element_path: str = os.path.join(directory, dir_element)
            if os.path.isdir(element_path):
                self.unify_files_permissions_in_directory_tree(element_path)
            elif os.path.isfile(element_path):
                self.unify_file_permissions(element_path)
            else:
                FileManager.logger.info(f'Encountered unsupported directory element {element_path}. '
                                        f'Program supports only directories and files.')

    def unify_file_permissions(self, file_path: str) -> None:
        file_status = os.stat(file_path)
        file_permissions: oct = oct(file_status.st_mode & 0o777)
        for unusual_perm in self.configurations[FileManager.unusual_file_permissions]:
            if oct(int(unusual_perm, 8)) == file_permissions:
                if self.is_global_file_permissions_unification or \
                        UserInputHandler.ask_if_unify_file_perm(file_path, file_permissions,
                                                                self.configurations[
                                                                    FileManager.default_file_permissions]):
                    os.chmod(file_path, self.configurations[FileManager.default_file_permissions])
                    break

    def replace_bad_chars_in_file_names(self) -> None:
        self.is_global_file_names_change = \
            UserInputHandler.ask_if_change_file_names_globally(self.target_dir,
                                                               self.configurations[FileManager.unwanted_chars],
                                                               self.configurations[FileManager.substitute_char])
        self.is_global_override_files = UserInputHandler.ask_if_change_file_names_override_globally()
        self.replace_bad_chars_in_file_names_in_directory_tree(self.target_dir)

    def replace_bad_chars_in_file_names_in_directory_tree(self, directory: str) -> None:
        bad_chars: List[str] = self.configurations[FileManager.unwanted_chars]
        sub_char: str = self.configurations[FileManager.substitute_char]
        for dir_path, _, file_names in os.walk(directory):
            for file_name in file_names:
                if any(char in file_name for char in bad_chars):
                    if self.is_global_file_names_change or \
                            UserInputHandler.ask_if_change_file_name(os.path.join(dir_path, file_name)):
                        old_file_path: str = os.path.join(dir_path, file_name)
                        new_file_name: str = ''.join(char if char not in bad_chars else sub_char for char in file_name)
                        new_file_path: str = os.path.join(dir_path, new_file_name)
                        if os.path.isfile(new_file_path):  # Such file already exists
                            if self.is_global_override_files or \
                                    UserInputHandler.ask_if_override_file_name(old_file_path, new_file_path):
                                try:
                                    os.remove(new_file_path)  # First remove file to be overwritten
                                except Exception as e:
                                    FileManager.logger.error(f'Could not remove file to be overwritten. ERROR: {e}')
                                    continue
                            else:
                                continue  # Do not change file name
                        try:
                            os.rename(old_file_path, new_file_path)
                        except Exception as e:
                            FileManager.logger.error(f'Could not rename file: {old_file_path}. ERROR: {e}')
                            continue

    def run(self) -> None:
        try:
            print(f'Moving files from source directories {" ,".join(self.src_dirs)} '
                  f'to target directory {self.target_dir}')
            self.move_files_from_sources_to_target()
            print(f'Removing empty files from target directory {self.target_dir} and its subdirectories')
            self.remove_empty_files_from_target()
            print(f'Removing temporary files from target directory {self.target_dir} and its subdirectories')
            self.remove_temp_files_from_target()
            print(f'Removing duplicated files from target directory {self.target_dir} and its subdirectories')
            self.remove_duplicates_from_target()
            print(f'Unifying files permissions in target directory {self.target_dir} and its subdirectories')
            self.unify_files_permissions()
            print(f'Changing bad characters ({self.configurations[FileManager.unwanted_chars]}) '
                  f'to substitute character {self.configurations[FileManager.substitute_char]} in all files of '
                  f'{self.target_dir} and its subdirectories')
            self.replace_bad_chars_in_file_names()
        except KeyboardInterrupt:
            print('Program closed')
            exit(0)
        except Exception as e:
            FileManager.logger.error(e)


def main() -> None:
    FileManager()


if __name__ == '__main__':
    main()
