# Download HTML versions of papers according to URLs in database

Given the location of a local Mendeley database file, and a group name (optional), the script `webpage.py` downloads the HTML pages of all papers in this group (or in this database file if group name not given) based on the URL information of papers in the database file. 

## Dependencies 
- xdotool, used by [automate-save-page-as](https://github.com/abiyani/automate-save-page-as)
- [automate-save-page-as](https://github.com/abiyani/automate-save-page-as). Clone and add its location to your `PATH` environment variable.
- a web browser supported by `automate-save-page-as`. Firefox works. Chromium is not supported. 

On Ubuntu, to install, run the following commands: 

	$ sudo apt install xdotool
	$ https://github.com/abiyani/automate-save-page-as.git
	$ echo "export PATH=$PATH:$(PWD)/automate-save-page-as" >> ~/.bashrc 
	$ source ~/.bashrc 


## Usage

	$ ./webpage.py -g "Group Name" /path/to/db.sqlite
    
It will save the HTML files to `<ID>.html` for each paper, where
`<ID>` is an integer. You can specify the output directory via `-o`
option, the default output dir is `"html_output"`. If the file already
exists, it will be skipped.

There are two ways to retrieve web url for a paper, either
automatically resolve the DOI of the paper from https://doi.org, or
by extracting the url in mendeley database. In case of both are
available, the preference will be determined by the `--prefer`
argument.
