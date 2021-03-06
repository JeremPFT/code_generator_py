import unittest

import os

from src.generator_ada_project import Generator_Ada_Project
from src.dsl_grammar import parse_input
from src.template_engine import Template_Engine
from src.uml_model import NoNameError

from src.utils import (
    directory,
    rmdir,
    dir_exists,
    text_files_match,
)

class Test_Unnamed_Project(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print(__class__)

    @classmethod
    def tearDownClass(cls):
        pass

    def test_no_name_project(self):
        input_file_name = "tests/test_002/test_002.dsl"
        self.assertRaises(NoNameError,
                          parse_input,
                          (input_file_name))

    # def test_no_name_project_2(self):
    #     input_file_name = "tests/test_002/test_002.dsl"
    #     project = parse_input(input_file_name)
    #     assert (False)
