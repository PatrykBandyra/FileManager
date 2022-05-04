FileManager

This program allows to:

- move files from source directories (and their subdirectories) into target directory (the source directories trees are
  not preserved - all files will be moved into top level directory); files can be moved globally or manually
  (one file at a time); in case of collision user can decide whether to preserve latest or oldest file
- remove empty files from target directory and its subdirectories; removal can happen in global or manual mode
- remove temporary files (defined by user in config.json) from target directory and its subdirectories;
  removal can happen in global or manual mode
- remove duplicated files (based on content) from target directory and its subdirectories;
  removal can happen in global or manual mode; user can decide what kind of sorting mechanism the script should use
  (sort by modification or creation date); only oldest (original) file will be preserved
- organize files permissions in target directory and its subdirectories; can happen in global or manual mode;
  user can define in config.json which permissions should be changed and what is a substitute permission
- replace bad characters (defined by user in config.json) in file names in target directory and its subdirectories;
  can happen in global or manual mode

This program can be used in 2 modes:

- In the first one, when "action" option (-a or --action) is "a",
  all functionalities of this script will be performed in order presented above
- In the second one, when "action" option is another one, the corresponding script functionality will be performed

How to run?

Files FileManager.py and UserInputHandler.py must be in the same directory.

Run command:

python FileManager.py -t <path_to_target_dir> -s <paths_to_src_dirs>... -c <path_to config.json> -a <action>

Source directories argument is only required when running "a" or "m" action (when file movement will be performed)