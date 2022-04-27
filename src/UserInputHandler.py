from typing import Tuple


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
    def ask_if_move_file(file_path, target_dir) -> bool:
        print(f'Move {file_path} to target directory: {target_dir} ?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_remove_empty_files_from_target_globally(target_dir) -> bool:
        print(f'Remove empty files from target directory {target_dir} globally?')
        return UserInputHandler.ask_yes_or_no_question()

    @staticmethod
    def ask_if_remove_temp_files_from_target_globally(target_dir) -> bool:
        print(f'Remove temporary files from target directory {target_dir} globally?')
        return UserInputHandler.ask_yes_or_no_question()
