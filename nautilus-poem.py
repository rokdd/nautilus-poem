from __future__ import print_function
from gi.repository import Nautilus, GObject
from typing import List
import yaml
import os
import sys

from urllib.parse import unquote

from pathlib import Path
import logging
import subprocess
import shlex
from urllib.parse import unquote

import ast
import operator
import sys

#taken from https://stackoverflow.com/questions/31999444/interpreting-a-python-string-as-a-conditional-statement
OPERATORS = {
    '<': operator.lt,
    '<=': operator.le,
    '>': operator.gt,
    '>=': operator.ge,
    '==': operator.eq,
    '!=': operator.ne,
    # 'in' is using a lambda because of the opposite operator order
    # 'in': (lambda item, container: operator.contains(container, item),
    'in': (lambda item, container: item in container),
    'contains': operator.contains,
    }


def process_conditionals(conditional_strings, variables):
    for conditional_string in conditional_strings:
        # Everything after first and op is part of second
        first, op, second = conditional_string.split(None, 2)

        resolved_operands = []
        for raw_operand in (first, second):
            try:
                resolved_operand = ast.literal_eval(raw_operand)
            except ValueError:  # If the operand is not a valid literal
                ve = sys.exc_info()
                try:
                    # Check if the operand is a known value
                    resolved_operand = variables[raw_operand]
                except KeyError:  # If the operand is not a known value
                    # Re-raise the ValueError
                    raise(ve[1], None, ve[2])

            resolved_operands.append(resolved_operand)

        yield (op, tuple(resolved_operands))


class NautilusPoem(GObject.GObject, Nautilus.MenuProvider):
    def init(self):

        self.logger = logging.getLogger()
        self.logger.debug("Init: Done")

    def load_yml(self,path,default_value):
        if os.path.exists(path):
            return yaml.safe_load(
            Path(path).read_text()
        )
        return default_value

    def load(self):
        HOME_DIR = os.environ["HOME"]
        # read config
        self.settings = self.load_yml(HOME_DIR + "/.config/nautilus-poem/config.yml",{"DEBUG":False})
        self.logger.debug(self.settings)
        # start debugging when True
        if self.settings["DEBUG"]:
            
            self.logger.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")

            stdout_handler = logging.StreamHandler(sys.stdout)
            stdout_handler.setLevel(logging.DEBUG)
            stdout_handler.setFormatter(formatter)

            file_handler = logging.FileHandler("/var/log/nautilus/nautilus-poem.log")
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)
            self.logger.addHandler(stdout_handler)
        self.items = self.load_yml(HOME_DIR + "/.config/nautilus-poem/items.yml",{})
        self.logger.debug(self.items)
        self.logger.debug("Load: Done")

    def get_file_items(
        self,
        files: List[Nautilus.FileInfo],
    ) -> List[Nautilus.MenuItem]:

        self.init()
        self.load()
        return self.iterate_recursive(self.items,files)

    def filter_keys(self, item, keys=[]):
        return {key: item[key] for key in keys if key in item.keys()}

    def iterate_recursive(self, items,files):
        menus = []

        # generate the inputs for the criteria  
        # https://gnome.pages.gitlab.gnome.org/nautilus-python/class-nautilus-python-file-info.html      
        env_vars={
            **{"os_"+k.lower():v for k,v in os.environ.items()},
            "items_count":len(files),
            "directory_count":len([f for f in files if f.is_directory()]),
            "files_count":len([f for f in files if not f.is_directory()]),
        }
        self.logger.debug(env_vars)
        # iterate the items tree through
        for item in items:
            # CHECK FOR THE CONDITION OF THE ITEM
            if "conditions" in item.keys():
                self.logger.debug(item["conditions"])
                conditionals = process_conditionals(item["conditions"], env_vars)

                try:
                    condition = all(OPERATORS[op](*operands)
                                    for op, operands in conditionals)
                except TypeError:
                    self.logger.warn("A literal in one of your conditionals is the wrong type. "
                        "If you can't see it, try running each one separately.")
                    break
                except ValueError:
                    self.logger.warn("An operand in one of your conditionals is neither a known "
                        "variable nor a valid literal. If you can't see it, try "
                        "running each one separately.")
                    break
                else:
                    if not condition:
                        self.logger.warn("Condition not met")
                        continue
                

            # filter the item only for the data which is really forwarded to nautilus
            # TODO: Load a template
            item_cleaned = {
                "label": "Default title",
                "tip": "",
                "icon": "",
                **self.filter_keys(item, ["name", "label", "tip", "icon"]),
            }
            if not "name" in item_cleaned.keys():
                # autogenerate a id from the data
                item_cleaned["name"] = (
                    self.__class__.__name__ \
                    + "::" \
                    + str(hash("-".join(list(item_cleaned.values()))))
                )
            self.logger.debug(item_cleaned)
            menu = Nautilus.MenuItem(**item_cleaned)
            menus.append(menu)

            # CHECK FOR ACTIONS
            if "subitems" in item.keys():
                submenu = Nautilus.Menu()
                menu.set_submenu(submenu)
                submenus = self.iterate_recursive(item["subitems"],files)
                for sb in submenus:
                    submenu.append_item(sb)
            #when it has a click registered we need to 
            elif "click" in item.keys():
                self.logger.debug("Activated "+item["click"])
                menu.connect("activate", self.menu_activate_cb,item["click"],files)

        return menus

    def get_background_items(
        self,
        current_folder: Nautilus.FileInfo,
    ) -> List[Nautilus.MenuItem]:
        # TODO: Implement background items
        submenu = Nautilus.Menu()
        submenu.append_item(
            Nautilus.MenuItem(
                name=self.__class__.__name__ + "::Bar2",
                label="Bar2 backgr",
                tip="",
                icon="",
            )
        )

        menuitem = Nautilus.MenuItem(
            name=self.__class__.__name__ + "::Foo2",
            label="Foo2 back",
            tip="",
            icon="",
        )
        menuitem.set_submenu(submenu)

        return [
            menuitem,
        ]

    def _shell(self, cmd) -> None:
        #filename = unquote(file.get_uri()[7:])

        #os.chdir(filename^
        
        cmd=shlex.split(cmd)

        process = subprocess.Popen(cmd,
                     stdout=subprocess.PIPE, 
                     stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        self.logger.debug(stdout)
        self.logger.error(stderr)

        #os.system("gnome-terminal")

    def menu_activate_cb(
        self,
        menu: Nautilus.MenuItem,
        cmd,
        files,
    ) -> None:
        
        files=[unquote(f.get_uri()[7:]) for f in files]


        #build the vars to replace
        env_vars={
            **{"OS_"+k.upper():v for k,v in os.environ.items()},
            "POEM_FILES": " ".join(files)}
        cmd=cmd.format(**env_vars)
        
        self.logger.debug("Execute "+cmd)
        self._shell(cmd)
