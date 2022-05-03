from typing import Tuple, List


class UserInputHandler:

    @staticmethod
    def ask_yes_or_no_question() -> bool:
        answer: str = input('Type "y" ("yes") or "n" ("no"): ')
        if answer.lower() == 'y' or answer.lower() == 'yes':
            return False
        elif answer.lower() == 'n' or answer.lower() == 'no':
            return True
        else:
            print('Invalid input. Enter answer again.')
            UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_perform_action_globally() -> bool:
        print('Ask about action for each file?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_move_files_globally() -> Tuple[bool, bool]:
        keep_latest_file: bool = True

        def ask_when_collision_keep_latest() -> bool:
            answer: str = input('Type "a" or "b": ')
            if answer.lower() == 'a':
                return True
            elif answer.lower() == 'b':
                return False
            else:
                print('Invalid input. Enter answer again.')
                ask_when_collision_keep_latest()

        is_global_move: bool = UserInputHandler.ask_if_perform_action_globally()
        if is_global_move:
            print('In case of file collision keep: \na) latest file\nb) oldest file')
            keep_latest_file = ask_when_collision_keep_latest()

        return is_global_move, keep_latest_file

    @staticmethod
    def ask_if_move_file(file_path: str, target_dir: str) -> bool:
        print(f'Move {file_path} to target directory: {target_dir} ?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_remove_empty_files_from_target_globally(target_dir: str) -> bool:
        print(f'Remove empty files from target directory {target_dir} globally?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_remove_temp_files_from_target_globally(target_dir: str) -> bool:
        print(f'Remove temporary files from target directory {target_dir} globally?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_remove_empty_file(file_path: str) -> bool:
        print(f'Remove empty file: {file_path} ?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_remove_temp_file(file_path: str) -> bool:
        print(f'Remove temporary file: {file_path} ?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_remove_dupl_files_from_target_globally(target_dir: str) -> bool:
        print(f'Remove duplicated files from target directory {target_dir} globally?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_remove_dupl_file(file_path: str) -> bool:
        print(f'Remove duplicated file: {file_path} ?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_sort_dupl_files_by_ctime() -> bool:
        print('Sort duplicated files by creation date? (Otherwise they will be sorted by modification date)')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_unify_files_perm_globally(target_dir: str, default_perm: str, strange_perms: List[str]) -> bool:
        print(f'Unify files permissions in target directory {target_dir} globally?\n'
              f'Permissions {strange_perms} will be replaced with {default_perm}')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_unify_file_perm(file_path: str, file_permissions: oct, default_perm: str) -> bool:
        print(f'Change file ({file_path}) permissions from {file_permissions} to {default_perm} ?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_change_file_names_globally(target_dir: str, bad_chars: List[str], substitute_char: str) -> bool:
        print(f'Change bad characters in file names in target directory {target_dir} globally? '
              f'Characters {bad_chars} will be replaced with {substitute_char}')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_change_file_name(file_path: str) -> bool:
        print(f'Change bad characters in file: {file_path} ?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_change_file_names_override_globally() -> bool:
        print('If changed file name already exists - override the existing file?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_override_file_name(old_file_path: str, new_file_path: str):
        print(f'{new_file_path} already exists. Override it with {old_file_path} ?')
        return UserInputHandler.ask_yes_or_no_question()
