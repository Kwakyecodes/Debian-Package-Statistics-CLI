"""Debian Package Statistics Command Line Tool"""

import argparse
import os
import re
import gzip
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Set

import requests

from exceptions.invalid_mirror_url_exception import InvalidMirrorURLException
from exceptions.architecture_not_found_exception import ContentFilesForArchitectureNotFound
from exceptions.invalid_count_exception import InvalidCountException


DEFAULT_DEBIAN_MIRROR_URL = "http://ftp.uk.debian.org/debian/dists/stable/main/"
DEFAULT_COUNT = 10
DEFAULT_OUTPUT_DIR = os.getcwd()
DEFAULT_OVERRIDE_EXISTING = False


def get_content_files(mirror_url: str) -> Dict[str, List[List[str]]]:
    """Returns a dictionary of architectures and a list of their 
    associated content files
    
    Args:
        mirror_url: URL of the debian mirror
        
    Returns:
        Dict[str, List[List[str]]]
        Example: {"amd64": [["file_name", "file_url"],
                            ...
                            ]
                }
    """
    content_files = dict()
    try:
        r = requests.get(mirror_url)
    except requests.exceptions.MissingSchema:
        raise InvalidMirrorURLException()
        
    html = r.text
    
    for line in html.split("\n"):
        file_name = re.findall("Contents-[a-z,1-9,-]+\.gz", f"{line}")
        if not file_name:
            continue
        file_name = file_name[0]
        file_url = mirror_url+file_name if mirror_url.endswith("/") else mirror_url+"/"+file_name
        architecture = re.findall("(?<=\-)([a-z, 1-9]+)(?=\.)", file_name)[0]
        
        if architecture in content_files:
            content_files[architecture].append([file_name, file_url])
        else:
            content_files[architecture] = [[file_name, file_url]
                                           ]
    return content_files


def download_content_file(
        file_url: str, output_dir: str,
        override_existing: bool) -> str:
    """Download content_file from file_url into output_dir
    
    Arguments:
        file_url: URL of content file
        output_dir: Folder for downloaded file. Default is the current working directory
        override_existing: Whether or not to use already downloaded content_file
    Returns:
        str: path of the content index file that was extracted from the downloaded file
    """
    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR
    
    base_name = os.path.basename(file_url)
    file_name = os.path.splitext(base_name)[0]
    
    gz_file = os.path.join(output_dir, base_name)
    extracted_file = os.path.join(output_dir, file_name)
    
    if file_name in os.listdir(output_dir) and (not override_existing):
        return extracted_file
    
    # Download content file from file_url
    with requests.get(file_url) as rq, open(gz_file, "wb") as file_buffer:
        file_buffer.write(rq.content)
    
    # Extract file from downloaded gz file
    with gzip.open(gz_file) as gz_buffer, open(extracted_file, "wb") as file_buffer:
        file_buffer.write(gz_buffer.read())
        
    return extracted_file


def parse_contents_index(extracted_file: str) -> Dict[str, Set[str]]:
    """Parse contents index file and returns dictionary with the package
    names and a set of their associated files
    
    Arguments:
        extracted_file: path of the file extracted from the downloaded gz file
    Returns:
        Dict[str, Set[str]]
        Example: {"package_name": (fileA, fileB, ...)}
    """
    with open(extracted_file, "r") as file_buffer:
        packages_dict = dict()
        for line in file_buffer:
            line = line.strip()
            parsed_line = " ".join(line.split()).split(" ")  # Remove large space between files and packages and split the two
            file_name, packages = parsed_line[0], parsed_line[-1]
            for package in packages.split(","):
                if file_name == "EMPTY_PACKAGE":
                    break
                if package in packages_dict:
                    packages_dict[package].add(file_name)
                else:
                    packages_dict[package] = {file_name}
        
    return packages_dict
                
                
def main(
        mirror_url: str, architecture: str, override_existing: bool, 
        output_dir: str, count: int) -> None:
    """Runs all the function of this command line tool. 
    
    Arguments:
        mirror_url: URL of the debian mirror
        architecture: system architecture
        override_existing: Whether or not to use already downloaded content_file
        output_dir: Folder for downloaded and extracted files
        count: limit of packages that are logged into the terminal
        
    Returns None
    """
    content_files = get_content_files(mirror_url=mirror_url)
    if architecture not in content_files:
        raise ContentFilesForArchitectureNotFound()
    
    if count < 0:
        raise InvalidCountException("count cannot be a negative integer")
    
    packages_dict = dict()
    
    with ThreadPoolExecutor() as executor:
        # Use threading to improve performace. It is most efficient when there are numerous downloads.
        results = [executor.submit(download_content_file, file_info[1], output_dir, override_existing)  # file_info[1] is file_url
                   for file_info in content_files[architecture]]
        
        for f in as_completed(results):
            packages_dict.update(parse_contents_index(f.result()))
            
    packages_file_count = {key: len(val) for key, val in sorted(packages_dict.items(), key = lambda ele: len(ele[1]), reverse=True)}
    
    print("\n","No.", " "*5, "Package", " "*45, "Number of Files")
    
    i = 1  # Counter to number the packages
    for package in packages_file_count:
        if count > 0:
            dist = 60-len(package)  # Spacing between package name and number of files
            print("", f"{i}", " "*5, f"{package}", " "*dist, f"{packages_file_count[package]}")
            count -= 1
            i += 1
        else:
            break  # End for loop after the print limit is reached 
        
    return None    


def cli_func() -> None:
    """Command line interface function"""
    
    parser = argparse.ArgumentParser(
        description=(
            "A command line tool for getting package statistics by parsing"
            " a contents index from a debian mirror given a system architecture."
        )
    )
    
    parser.add_argument(
        "arch",
        type=str,
        help="System architecture of content files you want to parse."
    )
    
    parser.add_argument(
        "-m",
        "--mirror_url",
        type=str,
        help="Mirrow URL from which to fetch the contents file."
    )
    
    parser.add_argument(
        "-v",
        "--override_existing",
        type=bool,
        help="Bool which determines whether or not to use already downloaded files"
    )
    
    parser.add_argument(
        "-o",
        "--output_dir",
        type=str,
        help="Path to folder where downloaded and extracted files should be kept."
    )
    
    parser.add_argument(
        "-c",
        "--count",
        type=int,
        help="Limit of packages that should be logged to the terminal."
    )
    
    args = parser.parse_args()
    
    mirror_url = args.mirror_url if args.mirror_url is not None else DEFAULT_DEBIAN_MIRROR_URL
    arch = args.arch if args.arch is not None else ""
    override_existing = args.override_existing if args.override_existing is not None else DEFAULT_OVERRIDE_EXISTING
    count = args.count if args.count is not None else DEFAULT_COUNT
    output_dir = args.output_dir if args.output_dir is not None else DEFAULT_OUTPUT_DIR
    
    main(
        mirror_url=mirror_url,
        architecture=arch,
        override_existing=override_existing,
        count=count,
        output_dir = output_dir
    )
    
    return None