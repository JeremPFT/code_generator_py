from typing import List
import os
import logging
from string import Formatter
from dataclasses import dataclass, field

from src.utils import (
    indent,
    directory,
)

class NoNameError(Exception):
    pass


def assert_no_empty_string(value):
    assert type(value) == str, \
        "given value is not a string {!r}".format(value)
    assert value != "", \
        "given string is empty"

def assert_type(value, type):
    msg = "given value is not a {!s}: {!r} is {!s}".format(type, value, type(value))

    if type.__name__ == "bool":
        assert value == False or value == True, msg
    else:
        assert type(value) == type, msg

def build_list_image(list):
    image = ""
    indent.incr()
    for item in list:
        image += indent.str() + str(item)
        if item != list[-1]:
            image += '\n'
    indent.decr()
    return image


class Project_Types:
    TYPE_STATIC_LIB = "static_library"
    TYPE_EXEC       = "executable"
    TYPE_TEST       = "test"

    VALUES = [TYPE_STATIC_LIB, TYPE_EXEC, TYPE_TEST]

    @staticmethod
    def is_valid(type):
        return type in Project_Types.VALUES

class Project:

    def __init__(self, name, output_directory, type, title, brief):

        self.log = logging.getLogger(__name__ + ":" + __class__.__name__)
        self.log.setLevel("DEBUG")

        self.log.info("initialize project with\n" + str(vars()))

        self.__set_name(name)
        self.__set_output_directory(output_directory)
        self.__set_type(type)
        self.__set_title(title)
        self.__set_brief(brief)

        self.__package = []

    @property
    def name(self):
        return self.__name

    def __set_name(self, name):
        assert_no_empty_string(name)
        self.__name = name

    @property
    def output_directory(self):
        return self.__output_directory

    def __set_output_directory(self, output_directory):
        assert_no_empty_string(output_directory)
        dir = output_directory.replace('"', '')
        self.__output_directory = directory(dir)

    @property
    def type(self):
        return self.__type

    def __set_type(self, type):
        assert Project_Types.is_valid(type), \
            "unknown project type: " + prj_type
        self.__type = type

    @property
    def title(self):
        return self.__title

    def __set_title(self, title):
        assert_no_empty_string(title)
        self.__title = title.replace('"', '')

    @property
    def brief(self):
        return self.__brief

    def __set_brief(self, brief):
        assert_no_empty_string(brief)
        self.__brief = brief.replace('"', '')

    def add_package(self, package_item):
        self.__package.append(package_item)

    @property
    def package(self):
        return self.__package

    def __str__(self):
        image  = "<{self.__class__.__name__}> {self.name!r}".format(self=self) + '\n'
        image += "in %s" % (self.output_directory) + '\n'
        image += "title {!r}".format(self.title) + '\n'
        image += "brief {!r}".format(self.brief) + '\n'
        image += build_list_image(self.__package)
        return image


class Element:
    '''
    see UML 2.4.1 Infrastructure section 9.15.1
    '''

    def __init__(self, owner = None, must_be_owned = False):
        self.log = logging.getLogger(__name__ + ":" + __class__.__name__)
        self.log.setLevel("DEBUG")

        self.log.info("initialize project with\n" + str(vars()))

        self.__owner         = None
        self.__owned_element = []
        self.__owned_comment = []
        self.__must_be_owned = False

        self.__set_owner(owner)
        self.__set_must_be_owned(must_be_owned)


    def __set_owner(self, owner):
        if owner == self:
            raise ValueError("an element can not own itself")
        self.__owner = owner

    @property
    def owner(self):
        return self.__owner

    def __set_must_be_owned(self, must_be_owned):
        assert_type(True, bool)

        if must_be_owned and (owner == None):
            raise ValueError("the element must be owned")

    @property
    def must_be_owned(self):
        return self.__must_be_owned

    def add_owned_element(self, element):
        assert element != None and type(element) == Element, \
            "element has to be an Element instance"
        self.owned_element.append(element)

    def add_owned_comment(self, comment):
        assert comment != None and type(comment) == Comment, \
            "comment has to be an Comment instance"
        self.owned_comment.append(comment)

    def all_owned_element(self):
        result = []

        for element in self.owned_element:
            result.append(element)
            result.append(element.all_owned_element)

        return result

    def __str__(self):
        return "<" + self.__class__.__name__ + ">"


class Comment(Element):
    '''
    see UML 2.4.1 Infrastructure section 9.5
    see UML 2.4.1 Suprastructure section 7.3.9
    '''

    def __init__(self, body, annoted_element = []):
        assert body != None and type(body) == str, \
            "comment body has to be a string"
        super.__init__()
        self.body = body
        self.annoted_element = []
        for element in annoted_element:
            self.annoted_element.append(element)

    def __str__(self):
        return super().__str__ + " " + self.body


class Multiplicity(Element):
    '''
    see UML 2.4.1 Infrastructure section 9.12

    if lower and upper are undefined, it is considered as 0..n, or *
    '''

    def __init__(self,
                 is_ordered = False,
                 is_unique = True,
                 lower = 1,
                 upper = 1):

        assert type(is_ordered) == bool, \
            "is_ordered must be a boolean"

        assert type(is_ordered) == bool, \
            "is_ordered must be a boolean"

        assert upper == None or upper > 0, \
            "upper must be an integer > 0"

        assert lower == None or lower >= 0, \
            "lower must be an integer >= 0"

        assert upper == None or ( lower != None and upper >= lower ), \
            "upper must greater than lower"

        self.is_ordered = is_ordered
        self.is_unique  = is_unique
        self.lower      = lower
        self.upper      = upper


class Named_Element(Element):
    '''see UML 2.4.1 Infrastructure section 9.14.1

    NOTES
    - the possibility of no name or empty name is ignored
    - a named element is considered as a packageable element
    '''

    def __init__(self, name, owner = None, must_be_owned = False):
        assert type(name) == str, \
            "name has to be a string"
        assert name != "", \
            "name has to be a no empty string"
        assert owner == None or Namespace in owner.__class__.__mro__, \
            "owner has to be a Namespace"
        assert type(must_be_owned) == bool, \
            "must_be_owned has to be a Boolean"

        super().__init__(owner = owner,
                         must_be_owned = must_be_owned)

        self.name = name

        self.qualified_name = name
        parent = self.owner
        while parent != None:
            self.qualified_name = parent.name + self.separator() + self.qualified_name
            parent = parent.owner

        # if owner == None:
        #     template = "building {self.__class__.__name__} " \
        #         + "named {self.name!r} without owner"
        #     print(template.format(self=self))
        # else:
        #     template = "building {self.__class__.__name__} " \
        #         + "named {self.name} with owner {owner.name}"
        #     print(template.format(self=self, owner=self.owner))

    def __str__(self):
        return super().__str__() + " {0.qualified_name!r}".format(self)

    def separator(self):
        'return separator used to form qualified name'
        return "::"


class VisibilityKind():
    PUBLIC = 0
    PRIVATE = 1
    PROTECTED = 2
    PACKAGE = 3

    def __init__(self, value):
        assert value == PUBLIC \
            or value == PROTECTED \
            or value == PRIVATE \
            or value == PACKAGE, \
            'unknown visibility: ' + str(value)

        self.value

    def __str__(self):
        if self.value == PUBLIC:
            return "+"
        elif self.value == PRIVATE:
            return "-"
        elif self.value == PROTECTED:
            return "#"
        elif self.value == PACKAGE:
            return "~"


class Namespace(Named_Element):
    '''
    see UML 2.4.1 Infrastructure section 9.14

    ignoring member field (which include member imported or inherited)
    '''

    def __init__(self, name, owner = None):
        super().__init__(name, owner)
        self._owned_member = []

    def find_element(self, name):
        for element in self._owned_member:
            if element.name == name:
                return element

        return None

    def add_owned_member(self, member):
        if member == None:
            raise Exception("member to add is None")
        self._owned_member.append(member)


class Package(Namespace):
    def __init__(self, name, owner = None):
        self.log = logging.getLogger(__name__ + ":" + __class__.__name__)
        self.log.setLevel("DEBUG")

        self.log.info("initialize project with\n" + str(vars()))

        super().__init__(name, owner)

        self.project = None


    def __str__(self):
        image = super().__str__()

        # if self.project == None:
        #     image += "no output file"
        # else:
        #     image += "output file: %s" %  \
        #     (self.project._output_directory \
        #      + "/src/" + self.name + ".ads")


        if len(self._owned_member) > 0:
            image += '\n'
            image += build_list_image(self._owned_member)
        else:
            image += " (no member)"

        return image


class Type_Definition(Named_Element):
    '''
    see UML 2.4.1 Superstructure section 7.3.52 Type
    '''
    pass


class Data_Type(Type_Definition):
    '''
    see UML 2.4.1 Superstructure section 7.3.11 DataType
    '''
    pass


class Enumeration(Data_Type):
    '''
    see UML 2.4.1 Superstructure section 7.3.16 Enumeration
    '''

    def __init__(self, owned_literal = []):
        super().__init__()
        self._owned_literal = []
        for literal in owned_literal:
            self.add_owned_member(literal)
            self._owned_literal.append(literal)

    def __str__(self):
        image = super().__str__() + " : "
        for literal in self._owned_literal:
            image += literal
            if literal != self._owned_literal[-1]:
                image += ", "


class Class(Namespace):
    '''
    see UML 2.4.1 Infrastructure section 9.14
    see UML 2.4.1 Superstructure section 7.3.7 Class
    see UML 2.4.1 Superstructure section 7.3.20 Generalization

    TODO class is a type or a namespace ?
    '''
    def __init__(self, name, owner, super_class_name = [], is_abstract = False):
        super().__init__(name, owner)

        self._is_abstract     = is_abstract
        self._dependance_list = []
        self._operation_list  = []
        self._property_list   = []
        self._owner           = owner

        self.__super_class      = []
        self.__super_class_name = []

        if len(super_class_name) > 0:
            if type(super_class_name) != str:
                raise Exception("super_class_name has to be a string")
            else:
                super_class = owner.find_element(super_class_name)
                if super_class == None:
                    raise Exception("super_class '%s' of '%s' not found in '%s'"
                                    % (super_class_name, self.name, owner.name))

    def add_property(self, property_item):
        self._property_list.append(property_item)

        if property_item.of_type.endswith("_vector"):
            self.add_operation(Operation.create_vector_count(property_item))
            self.add_operation(Operation.create_vector_get_by_index(property_item))
            self.add_operation(Operation.create_vector_has_item(property_item))
            self.add_operation(Operation.create_vector_add_item(property_item))

    def add_operation(self, operation_item):
        self._operation_list.append(operation_item)

    def __dependance_list_image(self):
        image = ""
        image += build_list_image(self._dependance_list)
        return image

    def __property_list_image(self):
        image = ""
        image += build_list_image(self._property_list)
        return image

    def __operation_list_image(self):
        image = ""
        image += build_list_image(self._operation_list)
        return image

    def __str__(self):

        image = "-" * 50 + '\n' + indent.str() + super().__str__()

        if self._super_class != None:
            image += " extends %s" % (self._super_class)

        if self._is_abstract:
            image += " is abstract"

        image += '\n'
        image += self.__dependance_list_image()
        if len(self._dependance_list) > 0:
            image += '\n'
        image += self.__property_list_image()
        if len(self._property_list) > 0 and len(self._operation_list) > 0:
            image += '\n'
        image += self.__operation_list_image()

        return image


class Operation(Named_Element):
    '''
    define procedure or function
    '''

    def __init__(self, name, is_query = False):
        super().__init__(name)
        self._is_query = is_query
        self._parameter_list = []
        self._returned_parameter_list = []

    def add_parameter(self, parameter):
        if parameter.__class__ != Parameter:
            raise Exception("class Parameter expected. Got " + str(parameter))

        if parameter.is_return():
            self._returned_parameter_list.append(parameter)
        else:
            self._parameter_list.append(parameter)

    def __return_image(self):
        image = ""

        if len(self._returned_parameter_list) > 0:
            image += " return "

        if len(self._returned_parameter_list) > 1:
            image += ("(")

        for param in self._returned_parameter_list:
            image += param.of_type

            if param != self._returned_parameter_list[-1]:
                image += ", "

        if len(self._returned_parameter_list) > 1:
            image += (")")

        return image

    def __str__(self):
        image = super().__str__()

        image += self.__return_image()

        if len(self._parameter_list) > 0:
            image += '\n'

        image += build_list_image(self._parameter_list)

        return image

    @staticmethod
    def create_vector_count(property_item):
        operation = Operation(name = property_item.name + "_count")

        param_self = Parameter(name      = "self",
                               direction = Parameter.DIRECTION_IN,
                               of_type   = "object_t")

        param_return = Parameter(name      = "result",
                                 direction = Parameter.DIRECTION_RETURN,
                                 of_type   = "natural")

        for param in (param_self, param_return):
            operation._parameter_list.append(param)

        return operation

    @staticmethod
    def create_vector_get_by_index(property_item):
        operation = Operation(name = "get_" + property_item.name)

        param_self = Parameter(name      = "self",
                               direction = Parameter.DIRECTION_IN,
                               of_type   = "object_t")

        param_index = Parameter(name      = "index",
                                direction = Parameter.DIRECTION_IN,
                                of_type   = "positive")

        item_type = property_item.of_type.replace("_vector", "")
        param_return = Parameter(name      = "result",
                                 direction = Parameter.DIRECTION_RETURN,
                                 of_type   = item_type)

        for param in (param_self, param_index, param_return):
            operation._parameter_list.append(param)

        return operation

    @staticmethod
    def create_vector_has_item(property_item):
        operation = Operation(name = "has_" + property_item.name)

        param_self = Parameter(name      = "self",
                               direction = Parameter.DIRECTION_IN,
                               of_type   = "object_t")

        param_value = Parameter(name      = "value",
                                direction = Parameter.DIRECTION_IN,
                                of_type   = "object_t")

        param_return = Parameter(name      = "result",
                                 direction = Parameter.DIRECTION_RETURN,
                                 of_type   = "boolean")

        for param in (param_self, param_value, param_return):
            operation._parameter_list.append(param)

        return operation

    @staticmethod
    def create_vector_add_item(property_item):
        operation = Operation(name = "add_" + property_item.name)

        param_self = Parameter(name      = "self",
                               direction = Parameter.DIRECTION_INOUT,
                               of_type   = "object_t")

        param_value = Parameter(name      = "value",
                               direction = Parameter.DIRECTION_IN,
                               of_type   = property_item.of_type)

        for param in (param_self, param_value):
            operation._parameter_list.append(param)

        return operation


class Typed_Element(Named_Element):
    '''
    Element with a type (extended by Parameter and Property)
    '''
    def __init__(self, name, of_type, default = None):
        super().__init__(name)
        self.of_type = of_type
        self.default = default

    def __str__(self):
        image = super().__str__() + " : %s" % (self.of_type)
        if self.default != None:
            image += " := %s" % (self.default)
        return image

class Parameter(Typed_Element):
    '''
    Parameter of an operation
    '''

    DIRECTION_IN     = "in"
    DIRECTION_OUT    = "out"
    DIRECTION_INOUT  = "inout"
    DIRECTION_RETURN = "return"

    DIRECTIONS = [DIRECTION_IN, DIRECTION_OUT, DIRECTION_INOUT, DIRECTION_RETURN]

    def __init__(self, name, of_type, direction = None, default = None):
        if direction == None:
            direction = Parameter.DIRECTION_IN

        if not direction in Parameter.DIRECTIONS:
            raise Exception("unknown parameter direction: " + mode)

        super().__init__(name, of_type, default)
        self._direction = direction

    def __str__(self):
        image = super().__str__() + " [%s]" % (self._direction)
        if self.default != None:
            image += " := %s" % (self.default)
        return image

    def is_return(self):
        return self._direction == Parameter.DIRECTION_RETURN


class Property(Typed_Element):
    '''
    see UML 2.4.1 Infrastructure section 11.3.5

    note
    if a property is owned by a class, it is an /attribute/ of the class
    '''

    def __init__(self, name, of_type, default = None):
        super().__init__(name, of_type, default)
        self.of_type = of_type
        self.default = default
        self.owning_class = None
        self.is_ordered = False
        self.is_unique = False

    def __str__(self):
        image = super().__str__()
        if self.default != None:
            image += " := %s" % (self.default)
        return image


class Dependance:

    MODE_WITH         = "with"
    MODE_USE          = "use"
    MODE_LIMITED_WITH = "limitedwith"

    MODES = [MODE_WITH, MODE_USE, MODE_LIMITED_WITH]

    def __init__(self, imported_unit, mode):
        if not mode in Dependance.MODES:
            raise Exception("unknown dependance mode: " + mode)

        self.imported_unit = imported_unit
        self.mode          = mode

    def __str__(self):
        image = "<" + self.__class__.__name__ + "> "

        if self.mode == Dependance.MODE_WITH:
            image += "with "
        elif self.mode == Dependance.MODE_USE:
            image += "use "
        elif self.mode == Dependance.MODE_LIMITED_WITH:
            image += "limited with "

        image += self.imported_unit

        return image
