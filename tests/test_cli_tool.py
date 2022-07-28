"""Unit tests for cli_tool.py file"""

import sys
sys.path.append("cli_tools")  # Add cli_tool to add that test_cli_tool.py can access exceptions
import os
import unittest

from cli_tool import (
    get_content_files,
    download_content_file,
    parse_contents_index,
    main,
)
from exceptions.architecture_not_found_exception import (
    ContentFilesForArchitectureNotFound
)
from exceptions.invalid_count_exception import (
    InvalidCountException
)
from exceptions.invalid_mirror_url_exception import (
    InvalidMirrorURLException
)


class CLITest(unittest.TestCase):
    def setUp(self):
        self.args = {
            "mirror_url": "http://ftp.uk.debian.org/debian/dists/stable/main/",
            "arch": "armel",
            "count": 10,
            "output_dir": "tests/files_dump",  # files_dump collects all files generated when testing
            "override_existing": False,
        }
        self.content_files = get_content_files(
                mirror_url=self.args["mirror_url"])
        self.file_url = self.content_files[self.args["arch"]][0][1]
        self.extracted_file_path = download_content_file(
                                        file_url=self.file_url,
                                        output_dir=self.args["output_dir"],
                                        override_existing=self.args["override_existing"]
                                        )
    
    def test_valid_get_content_files(self):
        self.assertIsInstance(get_content_files(
                                        mirror_url=self.args["mirror_url"]), 
                                    dict)
        
    def test_should_throw_mirror_invalid_url_exception(self):
        with self.assertRaises(InvalidMirrorURLException):
            get_content_files(mirror_url="")
            
    def test_valid_download_content_file(self):
        self.assertIsInstance(download_content_file(
                                file_url=self.file_url,
                                output_dir=self.args["output_dir"],
                                override_existing=self.args["override_existing"]), 
                              str)

    def test_valid_parse_contents_index(self):
        self.assertIsInstance(parse_contents_index(
                                extracted_file=self.extracted_file_path),
                              dict)
        
    def test_should_throw_architecture_not_found_exception(self):
        with self.assertRaises(ContentFilesForArchitectureNotFound):
            main(
                mirror_url=self.args["mirror_url"],
                architecture="",
                override_existing=self.args["override_existing"],
                count=self.args["count"],
                output_dir=self.args["output_dir"],
            )
            
    def test_should_throw_invalid_count_exception(self):
        with self.assertRaises(InvalidCountException):
            main(
                mirror_url=self.args["mirror_url"],
                architecture="amd64",
                override_existing=self.args["override_existing"],
                count=-20,
                output_dir=self.args["output_dir"],
            )
            
    def test_valid_main(self):
        self.assertIsNone(
            main(
                mirror_url=self.args["mirror_url"],
                architecture=self.args["arch"],
                override_existing=self.args["override_existing"],
                count=self.args["count"],
                output_dir=self.args["output_dir"],
            )    
        )
            
            
if __name__ == '__main__':
    unittest.main()