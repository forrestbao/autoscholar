# Rescue the data from the encrypted Mendeley Database
## Note
The script was built based on the link: https://eighty-twenty.org/2018/06/13/mendeley-encrypted-db . Use at your own risk.
## Requirements
* Python 3
* Mendeley version >= 1.19 with `stay signed in` checked
* pygdbmi

To install `pygdbmi` run:
```
pip install pygdbmi
```

## Running the tool
Help options:
```
usage: rescue.py [-h] --path PATH --database DATABASE [--attempts ATTEMPTS]
                 [--save SAVE] [--debug]

Rescue the data from the envrypted mendeley database.

optional arguments:
  -h, --help            show this help message and exit
  --path PATH, -p PATH  The mendeleydesktop file path.
  --database DATABASE, -db DATABASE
                        The encrypted database file path.
  --attempts ATTEMPTS, -t ATTEMPTS
                        The time of attempt, 2 times is default. Multiple
                        attempts needed due to the thread interleaving or
                        spurious opening of the database.
  --save SAVE, -s SAVE  Path to save the rescued database, current working
                        folder is default.
  --debug               Display debug information.
```
To run the script, the path to the `mendeleydesktop` and the path to database is required. The database file is usually located at :
```
~/.local/share/data/Mendeley Ltd./Mendeley Desktop/<some_id>@www.mendeley.com.sqlite
```
The script will backup your database file first to prevent potential data loss.

A typical run of the script looks like this:
```
python rescue.py --path /path/to/bin/mendeleydesktop --database ~/.local/share/data/"Mendeley Ltd."/"Mendeley Desktop"/<some_id>@www.mendeley.com.sqlite
```

## Verification
If the script outputs a successful message, the database should be readable using sqlite3. To verify the database, run:
```
$ sqlite3 <some_id>@www.mendeley.com.sqlite
SQLite version 3.29.0 2019-07-10 17:32:03
Enter ".help" for usage hints.
sqlite> .tables
CanonicalDocuments       DocumentZotero           NotDuplicates          
DataCleaner              Documents                Profiles               
DocumentCanonicalIds     EventAttributes          RemoteDocumentNotes    
DocumentContributors     EventLog                 RemoteDocuments        
DocumentDetailsBase      FileHighlightRects       RemoteFileHighlights   
DocumentFields           FileHighlights           RemoteFileNotes        
DocumentFiles            FileNotes                RemoteFolders          
DocumentFolders          FileReferenceCountsView  Resources              
DocumentFoldersBase      FileViewStates           RunsSinceLastCleanup   
DocumentKeywords         Files                    SchemaVersion          
DocumentNotes            Folders                  Settings               
DocumentReferences       Groups                   Stats                  
DocumentTags             HtmlLocalStorage         SyncTokens             
DocumentUrls             ImportHistory            ZoteroLastSync         
DocumentVersion          LastReadStates         
sqlite> .quit
```
If you see the message above, it means you succeeded in rescuing your data. You can do anything to the database now. 

## Issues
Due to the threading behavior or spurious opening of the database, the script does not always work, you can try to increase the number of attempts by add `-t` argument to specify the times of attempts. For example:
```
python rescue.py --path /path/to/bin/mendeleydesktop --database <some_id>@www.mendeley.com.sqlite -t 4
```