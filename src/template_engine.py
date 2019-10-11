#! python3

'''
Defines a simple template engine which should follow ada library Template Parser.
See http://docs.adacore.com/live/wave/aws/html/template_parser
'''


import os
import unittest


class Statement():
    def __init__(self, keyword):
        pass


class Filter():
    def __init__(self, keyword):
        lower_keyword = keyword.lower()
        if not lower_keyword in Filter.KEYWORDS:
            raise ValueError("invalid filter '%s'" % (keyword))
        self.index = Filter.KEYWORDS.index(lower_keyword)

    def process(self, argument):
        the_process = Filter.PROCESSING[self.index]
        return the_process(self, argument)

    def do_capitalize(self, argument):
        words = argument.split("_")
        splitted_image = []
        for word in words:
            splitted_image.append(word.capitalize())
        return "_".join(splitted_image)

    def do_upper(self, argument):
        return argument.upper()

    def do_double(self, argument):
        image = ""
        for car in argument:
            image += car
            image += car
        return image

    KEYWORDS = (
        "capitalize",
        "upper",
        "double",
    )

    PROCESSING = (
        do_capitalize,
        do_upper,
        do_double,
    )


class Template_Engine():
    def __init__(self, template_directory):
        self.tag_start = "@_"
        self.tag_stop = "_@"
        self.comment = "@@--"
        # to get a behavior like ada library template_parser

        self.__template_directory = ""
        self._set_template_directory(template_directory)

        self.dico = None

    def _set_template_directory(self, path):
        if type(path) != str:
            raise TypeError("template_directory has to be a string")

        if not os.path.exists(path):
            raise ValueError("template_directory not found: '%s'" % (path))

        self.__template_directory = path

    def _render_tag(self, string):
        string = string[len(self.tag_start):-len(self.tag_stop)]
        substrings = string.split(":")

        rendered = substrings[-1].lower()

        for key, value in self.dico.items():
            lower_key = key.lower()
            lower_value = value.lower()
            if lower_key in rendered:
                rendered = rendered.replace(lower_key, lower_value)
                break

        if len(substrings) > 1:
            for idx in range(len(substrings) - 2, -1, -1):
                filter = Filter(substrings[idx])
                rendered = filter.process(rendered)

        return rendered

    def render(self, file_name, dico):
        os.chdir(self.__template_directory)

        self.dico = dico

        template = open(file_name, "r")
        count    = 0
        rendered = []

        for line in template:
            count += 1

            if line.strip().startswith(self.comment):
                continue

            start_index = line.find(self.tag_start)
            stop_index  = line.rfind(self.tag_stop)
            shift       = len(self.tag_stop)

            if start_index != -1 and stop_index != -1:
                rendered.append(line[:start_index]
                                + self._render_tag(line[start_index:stop_index + shift])
                                + line[stop_index + shift:])

            elif start_index != -1 and stop_index == -1:
                print("WARNING line %s, tag not close :" + line[start_index:] )

            elif start_index == -1 and stop_index != -1:
                print("WARNING line %s, closing tag not open")

            else:
                rendered.append(line)

        count = 0

        for line in rendered:
            count += 1
            # print("line %s: '%s'" % (str(count), line.replace("\n", "")))
            print(line.replace("\n", ""))


if __name__ == '__main__':
    template_dir = "d:/Users/jpiffret/AppData/Roaming/Dropbox/projets_perso/ada/code_generator_py/templates"
    te = Template_Engine(template_dir)

    te.render("lib_project.gpr", {
        "Project_Name" : "essai_1_azerty",
        "A" : "zerty",
        "b" : "ercredi",
    })
