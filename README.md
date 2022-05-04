# FileManager

This program allows to:

- move files from source directories (and their subdirectories) into target directory (the source directories trees are not preserved - all files will be moved into top level directory)
- remove empty files from target directory and its subdirectories
- remove temporary files (defined by user in config.json) from target directory and its subdirectories
- remove duplicated files (based on content) from target directory and its subdirectories
- organize files permissions in target directory and its subdirectories
- replace bad characters (defined by user in config.json) in file names in target directory and its subdirectories

This program can be used in 2 modes:

- In the first one, when "action" option (-a or --action) is "a", all functionalities of this script will be performed in order presented above
- In the second one, when "action" option is another one, the corresponding script functionality will be performed

### How to run?

Files FileManager.py and UserInputHandler.py must be in the same directory.

```shell
python FileManager.py -t <path_to_target_dir> -s <paths_to_src_dirs>... -c <path_to config.json> -a <action>
```

