import os

from src.dsl_grammar import test_grammar
from src.lexer import test_lexer
from src.output_ada import Output_Ada

data = '''
project project_name
output_directory "c:\"
-- a basic example to test the parser
end_project
    '''

data = open("input.dsl", "r").read()
prj = test_grammar(data)
# if prj != None:
#     print(os.linesep + ("=" * 60) + os.linesep)
#     print(prj)
#     print(os.linesep + "=" * 60)
generator = Output_Ada()
generator.output(prj)