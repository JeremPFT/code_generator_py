#! python3


''' Defines input grammar.

TODO define yas snippets to generate list rules
'''


import os
import ply.yacc as yacc

from src.lexer import (
    tokens,
    find_column,
    reset_lexer
)

from src.uml_model import *

from src.utils import dbg

'''
(fset 'copy-grammar-rule
[?\C-s ?: ?\C-j ?  ?\' ?\' ?\' return ?\M-f ?\M-b ?\C-  ?\C-s ?\' ?\' ?\' ?\C-a ?\M-w ?\C-x ?o ?\C-y ?\C-x ?o])
'''

'''
project_item                       : project_init project_content project_close
project_init                       : PROJECT IDENTIFIER
project_content                    : output_directory project_type package_list
project_close                      : END PROJECT IDENTIFIER SEMICOLON
project_close                      : END PROJECT SEMICOLON
package_list                       :
package_list                       | package_list package
package                            : package_init package_content package_close
package_init                       : PACKAGE IDENTIFIER
package_content                    : dependance_list packageable_element_list
package_close                      : END PACKAGE IDENTIFIER SEMICOLON
package_close                      : END PACKAGE SEMICOLON
dependance_list                    :
dependance_list                    : dependance_list dependance
dependance                         : WITH IDENTIFIER
dependance                         : USE IDENTIFIER
dependance                         : LIMITED WITH IDENTIFIER
packageable_element_list           :
packageable_element_list           : packageable_element_list packageable_element
packageable_element                : operation
                                   | type_item
type_item                          : exception_block                 // TODO
                                   | value_object
value_object                       : value_object_init value_object_content value_object_close
value_object_init                  : value_object_init_abstract_inherit
                                   | value_object_init_abstract
                                   | value_object_init_inherit
                                   | value_object_init_simple
value_object_init_abstract_inherit : ABSTRACT VALUE_OBJECT IDENTIFIER LPAREN IDENTIFIER RPAREN
value_object_init_abstract         : ABSTRACT VALUE_OBJECT IDENTIFIER
value_object_init_inherit          : VALUE_OBJECT IDENTIFIER LPAREN IDENTIFIER RPAREN
value_object_init_simple           : VALUE_OBJECT IDENTIFIER
value_object_content               : dependance_list feature_list
value_object_close                 : END VALUE_OBJECT IDENTIFIER SEMICOLON
value_object_close                 : END VALUE_OBJECT SEMICOLON
feature_list                       :
feature_list                       : feature_list feature
feature                            : property SEMICOLON
                                   | operation SEMICOLON
operation                          : operation_init parameter_list operation_return
operation_init                     : OPERATION IDENTIFIER
operation_return                   :
operation_return                   : RETURN IDENTIFIER
parameter_list                     :
parameter_list                     : LPAREN parameter_item RPAREN
parameter_list                     : LPAREN parameter_item_list parameter_item RPAREN
parameter_item_list                : parameter_item SEMICOLON
parameter_item_list                : parameter_item_list parameter_item
parameter_item                     : IDENTIFIER COLON direction IDENTIFIER
direction                          : INOUT
                                   | OUT
                                   | IN
property                           : IDENTIFIER COLON IDENTIFIER
project_type                       : TYPE IDENTIFIER SEMICOLON
output_directory                   : OUTPUT_DIRECTORY string
string                             : string AMP STRING_VALUE
string                             : STRING_VALUE
'''

def check_closing_name(got, instance):
    if got != instance.name:
        msg = "WARNING closed {!r} {!r} doesn't match opened {!r}"
        msg = msg.format(instance.__class__.__name__, got, instance.name)
        print(msg)

#
# - project
#

def p_project_item(p):
    '''
    project : project_init project_content project_close
    '''
    p[0] = p[1]

def p_project_init(p):
    '''
    project_init : PROJECT IDENTIFIER output_directory project_type readme_content
    '''
    p[0] = Project(name              = p[2],
                   output_directory  = p[3],
                   type              = p[4],
                   title             = p[5][0],
                   brief             = p[5][1],
    )
    p.parser.current_project = p[0]

def p_project_init_unnamed(p):
    '''
    project_init : PROJECT unnamed_project output_directory project_type readme_content
    '''
    print("p_project_init_unnamed")
    message = "ERROR unnamed project line {}".format(p.lineno(2))
    p.parser.log.fatal(message)
    raise NoNameError(message)

def p_unnamed_project(p):
    '''
    unnamed_project :
    '''
    p[0] = p.lineno(0)

def p_readme_content(p):
    '''
    readme_content : README_TITLE string README_BRIEF string
    '''
    p[0] = (p[2], p[4])

def p_project_content(p):
    '''
    project_content : package_list
    '''

    for package_item in p[1]:
        p.parser.current_project.add_package(package_item)

def p_project_close_with_name(p):
    '''
    project_close : END PROJECT IDENTIFIER SEMICOLON
    '''
    name = p[3]
    check_closing_name(got = name, instance = p.parser.current_project)

def p_project_close(p):
    '''
    project_close : END PROJECT SEMICOLON
    '''
    pass

#
# - package
#

def p_package_list_empty(p):
    '''
    package_list :
    '''
    p[0] = []

def p_package_list_more(p):
    '''
    package_list : package_list package_item
    '''
    p[1].append(p[2])
    p[0] = p[1]

def p_package_item(p):
    '''
    package_item : package_init package_content package_close
    '''
    p[0] = p[1]

def p_package_init(p):
    '''
    package_init : PACKAGE IDENTIFIER
    '''
    p[0] = Package(name = p[2])
    p.parser.current_package = p[0]

def p_package_content(p):
    '''
    package_content : dependance_list packageable_element_list
    '''
    p[-1].dependance_list          = p[1]
    p[-1].packageable_element_list = p[2]

def p_package_close_with_name(p):
    '''
    package_close : END PACKAGE IDENTIFIER SEMICOLON
    '''
    name = p[3]
    check_closing_name(got = name, instance = p.parser.current_package)

def p_package_close(p):
    '''
    package_close : END PACKAGE SEMICOLON
    '''
    pass

#
# - dependancy
#

def p_dependance_list_empty(p):
    '''
    dependance_list :
    '''
    p[0] = []

def p_dependance_list_more(p):
    '''
    dependance_list : dependance_list dependance
    '''
    p[1].append(p[2])
    p[0] = p[1]

def p_dependance_with(p):
    '''
    dependance : WITH IDENTIFIER
    '''
    p[0] = Dependance(mode = p[1], imported_unit = p[2])

def p_dependance_use(p):
    '''
    dependance : USE IDENTIFIER
    '''
    p[0] = Dependance(mode = p[1], imported_unit = p[2])

def p_dependance_limited_with(p):
    '''
    dependance : LIMITED WITH IDENTIFIER
    '''
    p[0] = Dependance(mode = p[1] + p[2], imported_unit = p[3])

#
# - packageable_element
#

def p_packageable_element_list_empty(p):
    '''
    packageable_element_list :
    '''
    p[0] = []

def p_packageable_element_list_more(p):
    '''
    packageable_element_list : packageable_element_list packageable_element
    '''
    p[1].append(p[2])
    p[0] = p[1]

def p_packageable_element_item(p):
    '''
    packageable_element : operation
                        | type_item
                        | package_item
    '''
    p[0] = p[1]

    # TODO.
    # add package_item, dependancy, constraint

def p_type_item(p):
    '''
    type_item : value_object
              | exception_block
    '''
    p[0] = p[1]

def p_exception_block(p):
    '''
    exception_block : EXCEPTIONS exception_list exception_item END EXCEPTIONS SEMICOLON
    '''

def p_exception_list_empty(p):
    '''
    exception_list :
    '''
    p[0] = []

def p_exception_list_more(p):
    '''
    exception_list : exception_list exception_item
    '''
    p[1].append(p[2])
    p[0] = [1]

def p_exception_item(p):
    '''
    exception_item : IDENTIFIER
    '''
    p[0] = p[1]

#
# - value_object
#

def p_value_object_item(p):
    '''
    value_object : value_object_init    \
                   class_attribute_list \
                   dependance_list      \
                   value_object_content \
                   value_object_close
    '''
    vo, attr, dependance, feature = p[1], p[2], p[3], p[4]

    vo.is_abstract = attr["is_abstract"]

    for item in attr["super_class"]:
        vo.add_super_class(item)

    for item in dependance:
        vo.add_dependance(item)

    if feature != None:
        for item in feature:
            vo.add_feature(item)

    p[0] = vo

def p_value_object_init(p):
    '''
    value_object_init : VALUE_OBJECT IDENTIFIER
    '''
    data = {
        "name"  : p[2],
        "owner" : p.parser.current_package,
    }

    result = Class(**data)

    p.parser.current_class = result

    p[0] = result


def p_class_attribute_list_empty(p):
    '''
    class_attribute_list :
    '''
    p[0] = {
        "is_abstract": False,
        "super_class": []
    }

def p_class_attribute_list_more(p):
    '''
    class_attribute_list : IS class_attribute_item
    '''

def p_class_attribute_item_abstract(p):
    '''
    class_attribute_item : ABSTRACT
    '''
    p.parser.current_class.is_abstract = True

def p_class_attribute_item_inheritance(p):
    '''
    class_attribute_item : NEW IDENTIFIER
    '''
    p.parser.current_class.add_super_class_name(p[2])

    # TODO allow qualified name for parent
    # TODO allow multiple parents

def p_value_object_content(p):
    '''
    value_object_content : feature_list
    '''

    feature = p[1]

    for item in feature:
        if item.__class__.__name__ == Property.__name__:
            p[-1].add_property(item)
        elif item.__class__.__name__ == Operation.__name__:
            p[-1].add_operation(item)

def p_value_object_close_with_name(p):
    '''
    value_object_close : END VALUE_OBJECT IDENTIFIER SEMICOLON
    '''
    name = p[3]
    check_closing_name(got = name, instance = p.parser.current_class)

def p_value_object_close(p):
    '''
    value_object_close : END VALUE_OBJECT SEMICOLON
    '''
    pass

#
# - feature
#

def p_feature_list_none(p):
    '''
    feature_list :
    '''
    p[0] = []

def p_feature_list_more(p):
    '''
    feature_list : feature_list feature_item
    '''
    p[1].append(p[2])
    p[0] = p[1]

def p_feature_item(p):
    '''
    feature_item : property SEMICOLON
                 | operation SEMICOLON
    '''
    p[0] = p[1]

#
# - operation
#

def p_operation_item(p):
    '''
    operation : operation_init parameter_list operation_return
    '''

    operation     = p[1]
    parameters    = p[2]
    returned_type = p[3]

    for parameter in parameters:
        operation.add_parameter(parameter)

    if returned_type != None:
        operation.add_parameter(returned_type)

    p[0] = operation

def p_operation_init(p):
    '''
    operation_init : OPERATION IDENTIFIER
    '''
    p[0] = Operation(name = p[2])

def p_operation_return_none(p):
    '''
    operation_return :
    '''
    p[0] = None

def p_operation_return_one(p):
    '''
    operation_return : RETURN IDENTIFIER
    '''
    p[0] = Parameter(name      = "result",
                     of_type   = p[2],
                     direction = Parameter.DIRECTION_RETURN)

def p_parameter_list(p):
    '''
    parameter_list :
    '''
    p[0] = []

def p_parameter_list_one(p):
    '''
    parameter_list : LPAREN parameter_item RPAREN
    '''
    p[0] = [p[2]]

def p_parameter_list_more(p):
    '''
    parameter_list : LPAREN parameter_item_list parameter_item RPAREN
    '''
    p[0] = p[2]
    p[0].append(p[3])

def p_parameter_item_list_one(p):
    '''
    parameter_item_list : parameter_item SEMICOLON
    '''
    p[0] = [p[1]]

def p_parameter_item_list_more(p):
    '''
    parameter_item_list : parameter_item_list parameter_item
    '''
    p[0] = p[1]
    p[0].append(p[2])

def p_parameter_item(p):
    '''
    parameter_item : IDENTIFIER COLON direction IDENTIFIER
    '''
    p[0] = Parameter(name = p[1], direction = p[3], of_type = p[4])

def p_direction(p):
    '''
    direction : INOUT
              | OUT
              | IN
    '''
    p[0] = p[1]

#
# - implementation
#

# pseudocode def p_implementation_from_file(p):
# pseudocode     '''
# pseudocode     implementation : IMPLEMENTATION string SEMICOLON
# pseudocode     '''
# pseudocode
# pseudocode     implementation_file = open(p[2])
# pseudocode
# pseudocode     # TODO following is pseudo code
# pseudocode
# pseudocode     declaration = substring(path = implementation_file,
# pseudocode                             from = position_of ("[^a-z_]is[^a-z_]"),
# pseudocode                             end  = position_of ("[^a-z_]begin[^a-z_]"))
# pseudocode
# pseudocode     body = substring(path = implementation_file,
# pseudocode                      from = position_of ("[^a-z_]begin[^a-z_]"),
# pseudocode                      end  = last_position_of ("[^a-z_]end[^a-z_]"))
# pseudocode
# pseudocode def p_implementation(p):
# pseudocode     '''
# pseudocode     implementation : declaration_item body_item
# pseudocode     '''
# pseudocode     pass
# pseudocode
# pseudocode def p_declaration(p):
# pseudocode     '''
# pseudocode     declaration_item : DECLARATION declaration_content
# pseudocode     '''

#
# - property
#

def p_property_item(p):
    '''
    property : IDENTIFIER COLON IDENTIFIER
    '''
    p[0] = Property(name = p[1], of_type = p[3])

#
# - others
#

def p_project_type(p):
    '''
    project_type : TYPE IDENTIFIER SEMICOLON
    '''
    prj_type = p[2]

    if not prj_type in Project_Types.VALUES:
        msg = "!! SyntaxError: project type {!r} undefined line {}"
        msg = msg.format(prj_type, p.lineno(1))
        print(msg)
        raise SyntaxError

    p[0] = p[2]

def p_output_directory(p):
    '''
    output_directory : OUTPUT_DIRECTORY string SEMICOLON
    '''
    p[0] = p[2]

def p_string_one_or_more(p):
    '''
    string : string AMP STRING_VALUE
    '''
    left  = p[1].replace('"', '')
    right = p[3].replace('"', '')
    p[0]  = '"' + left + right + '"'

def p_string_one(p):
    '''
    string : STRING_VALUE
    '''
    p[0] = p[1]

def p_error(p):
    if p == None:
        print("!! SyntaxError: end of file")
        return

    # if p.parser.error != None:
    #     print(str(p.parser.error))

    #     tok = None
    #     while True:
    #         tok = parser.token()
    #         if tok == None:
    #             break
    #         else:
    #             print("ignoring token line {!s}".format(tok.lineno))
    # else:
    #     print("!! SyntaxError in input")
    #     message = "line %s: unexpected %s %s" % (str(p.lineno), str(p.type), str(p))
    #     print(message)

def parse_input(input_path):
    parser = yacc.yacc(debug = False)
    parser.error             = None
    parser.current_project   = None
    parser.current_package   = None
    parser.current_class     = None
    parser.current_procedure = None

    logging.basicConfig(level=logging.DEBUG)
    parser.log = logging.getLogger(__name__)

    reset_lexer()

    input_file_name = directory(input_path)
    input_file = open(input_file_name, "r")
    parser.input_data = input_file.read()
    input_file.close()
    project = parser.parse(
        input = parser.input_data,
        tracking = True,
    )
    return project

def test_grammar(data):
    result = parser.parse(data, debug = False)
    print("return object " + str(type(result)))
    return result

if __name__ == '__main__':
    prj = test_grammar()
    if prj != None:
        print(os.linesep + ("=" * 60) + os.linesep)
        print(prj)
        print(os.linesep + "=" * 60)
