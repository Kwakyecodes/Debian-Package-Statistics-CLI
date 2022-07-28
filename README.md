# Debian Package Statistics Command Line Tool
A command line tool for getting package statistics by parsing a contents index from a debian mirror given a system architecture.

Python version: 3.9.13


### Requirements 
Requirements for this project can be found in requirements.txt. To get the requirements, run:
```
$ pip3 install -r requirements.txt
```


### Usage
```
package_statistics.py [-h] [-m MIRROR_URL] [-v OVERRIDE_EXISTING] [-o OUTPUT_DIR] [-c COUNT] arch

A command line tool for getting package statistics by parsing a contents index from a debian mirror given a system architecture.

positional arguments:
  arch                  System architecture of content files you want to parse.

optional arguments:
  -h, --help            show this help message and exit
  -m MIRROR_URL, --mirror_url MIRROR_URL
                        Mirrow URL from which to fetch the contents file.
  -v OVERRIDE_EXISTING, --override_existing OVERRIDE_EXISTING
                        Bool which determines whether or not to use already downloaded files
  -o OUTPUT_DIR, --output_dir OUTPUT_DIR
                        Path to folder where downloaded and extracted files should be kept.
  -c COUNT, --count COUNT
                        Limit of packages that should be logged to the terminal.
```

You can access this information by running:
```
$ python package_statistics.py -h
```


### Testing 
Unittest was used to test this command line tool.
Run test_cli_tool.py inside the tests directory to test the script
```
.....
 No.       Package                                               Number of Files
 1       devel/piglit                                                  51784
 2       science/esys-particle                                         18015
 3       libdevel/libboost1.74-dev                                     14333
 4       math/acl2-books                                               12668
 5       golang/golang-1.15-src                                        9015
 6       libdevel/liboce-modeling-dev                                  7457
 7       net/zoneminder                                                7002
 8       libdevel/paraview-dev                                         6178
 9       kernel/linux-headers-5.10.0-16-amd64                          6150
 10       kernel/linux-headers-5.10.0-13-amd64                          6149
..
----------------------------------------------------------------------
Ran 7 tests in 12.077s

OK
```


### Time spent
Time spent learning important topics for project ~ 50 minutes
Time spent writing code ~ 2 hours 30 minutes
Total time spent on exercise ~ 3 hours 20 minutes