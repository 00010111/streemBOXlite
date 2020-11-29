# streemBOXlite
## parse streemfs.db file to extract useful data and match filename to cache id
The desktop client of box.com created the streemfs SQLite database file. streemBOXlite parses this file to extract useful data from it and aviod manunal work.
Probably most useful will be the match of file name to cache id.

## Usage
Option | Explanation
--- | ---
-p --path \<PATH\> | Path to the folder containing the acquiered streemfs.db file, output will show cache file path Windows as %USERPROFILE% "+s_path_box_cache_w+" as Path unless -U is used to overwrite the default
-l --localcache \<PATH\> | If you acquiered the cache folder (%USEROROFILE%AppData\Local\Box\Box\cache) from the original system you can provide its local path. Only valid if -p option is used
-u --users \<PATH\> | Path to the acquiered Users Folder, Output will show cache file path windows as %SYSTEMDRIVE%\\Users\$USERNAME\\"+s_path_box_cache_w+" as Path unless -S is used to overwrite the default\n\tstreemfs.db and cache folder are searched at default path, if not found at the default location, the given Users directory is searched recursivly for a "+s_file_streemfs+" file and a folder named cache. In both cases ONLY THE FIRST HIT will be processed.
-U --USERPROFILE \<VALUE\> | override %USERPROFILE% in output of -p option
-S --SYSTEMDRIVE \<VALUE\> | override %SYSTEMDRIVE% in output of -u option
-c --csv | write outout as csv file
-j --json | write output to json file
-q --quiet | do not print results to stdout
-v --verbose | print out status messages like successful database access and writing output files to stdout
-s --short | short output option only giving file name, cache file name (aka cacheID), File or no File, and Create,Modified Date/Time
-o --output \<PATH\> | path to output directory
-h --help | print usage information

If field "CacheFileLocalPath" contains "UNVALIDATED" as prefix the corresponding cache file could not be found at the shown path



## Examples
```
# run streemBOXlite providing a path to the folder containing the streemfs.db file
python3 ./streemBOXlite.py -p ./evidence/box/data/

# run streemBOXlite providing a path to the acquired users folder
python3 ./streemBOXlite.py -u ./box_acquisition/C/Users/

# run streemBOXlite providing a path to the folder containing the streemfs.db file, creating csv and json result file
# printing status messages to stdout, surpressing parsed database output to stdout 
python3 ./streemBOXlite.py -p ./evidence/box/data/ -c -j -v -q

# run streemBOXlite providing a path to the folder containing the streemfs.db file, creating json result file
# overwrite local cache path
python3 ./streemBOXlite.py -p ./evidence/box/data/ -j -l ./evidence/box/cache/ 

# run streemBOXlite providing a path to the folder containing the streemfs.db file, using the short output action
python3 ./streemBOXlite.py -p ./evidence/box/data/ -s
```

## Author
* Twitter: [@b00010111](https://twitter.com/b00010111)
* Blog: https://00010111.at/

## License
* Free to use, reuse and redistribute for everyone.
* No Limitations.
* Of course attribution is always welcome but not mandatory.

## Bugs, Discussions, Feature requests, contact
* open an issue
* contact me via twitter

## Change History
 * Version 0.0051:
    * fix writing json file
 * Version 0.0050:
    * initial release