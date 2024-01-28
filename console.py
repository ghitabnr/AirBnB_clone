#!/usr/bin/python3
"""Module for the entry point of the command interpreter."""

import cmd
from models.base_model import BaseModel
from models import storage
import re
import json


class HBNBCommand(cmd.Cmd):

    """Class for the command interpreter."""

    prompt = "(hbnb) "

    def default(self, ln):
        """Catch commands if nothing else mches then."""
        # print("DEF:::", ln)
        self._precmd(ln)

    def _precmd(self, ln):
        """Intercepts commands to test for class.syntax()"""
        # print("PRECMD:::", ln)
        mch = re.search(r"^(\w*)\.(\w+)(?:\(([^)]*)\))$", ln)
        if not mch:
            return ln
        cName = mch.group(1)
        method = mch.group(2)
        args = mch.group(3)
        mch_uid_and_args = re.search('^"([^"]*)"(?:, (.*))?$', args)
        if mch_uid_and_args:
            uid = mch_uid_and_args.group(1)
            attr_or_dict = mch_uid_and_args.group(2)
        else:
            uid = args
            attr_or_dict = False

        attr_and_value = ""
        if method == "update" and attr_or_dict:
            mch_dict = re.search('^({.*})$', attr_or_dict)
            if mch_dict:
                self.update_dict(cName, uid, mch_dict.group(1))
                return ""
            mch_attr_and_value = re.search(
                '^(?:"([^"]*)")?(?:, (.*))?$', attr_or_dict)
            if mch_attr_and_value:
                attr_and_value = (mch_attr_and_value.group(
                    1) or "") + " " + (mch_attr_and_value.group(2) or "")
        command = method + " " + cName + " " + uid + " " + attr_and_value
        self.onecmd(command)
        return command

    def update_dict(self, cName, uid, s_dict):
        """Helper method for update() with a dictionary."""
        s = s_dict.replace("'", '"')
        d = json.loads(s)
        if not cName:
            print("** class name missing **")
        elif cName not in storage.classes():
            print("** class doesn't exist **")
        elif uid is None:
            print("** instance id missing **")
        else:
            key = "{}.{}".format(cName, uid)
            if key not in storage.all():
                print("** no instance found **")
            else:
                attrs = storage.attrs()[cName]
                for attr, value in d.items():
                    if attr in attrs:
                        value = attrs[attr](value)
                    setattr(storage.all()[key], attr, value)
                storage.all()[key].save()

    def do_EOF(self, ln):
        """Handles End Of File character.
        """
        print()
        return True

    def do_quite(self, ln):
        """Exits the program.
        """
        return True

    def empty_ln(self):
        """Doesn't do anything on ENTER.
        """
        pass

    def do_create(self, ln):
        """Creates an instance.
        """
        if ln == "" or ln is None:
            print("** class name missing **")
        elif ln not in storage.classes():
            print("** class doesn't exist **")
        else:
            nInstance = storage.classes()[ln]()
            nInstance.save()
            print(nInstance.id)

    def do_show(self, ln):
        """Prints the string representation of an instance.
        """
        if ln == "" or ln is None:
            print("** class name missing **")
        else:
            wrd = ln.split(' ')
            if wrd[0] not in storage.classes():
                print("** class doesn't exist **")
            elif len(wrd) < 2:
                print("** instance id missing **")
            else:
                instKey = "{}.{}".format(wrd[0], wrd[1])
                if instKey not in storage.all():
                    print("** no instance found **")
                else:
                    print(storage.all()[instKey])

    def do_destroy(self, ln):
        """Deletes an instance based on the class name and id.
        """
        if ln == "" or ln is None:
            print("** class name missing **")
        else:
            wrd = ln.split(' ')
            if wrd[0] not in storage.classes():
                print("** class doesn't exist **")
            elif len(wrd) < 2:
                print("** instance id missing **")
            else:
                instKey = "{}.{}".format(wrd[0], wrd[1])
                if instKey not in storage.all():
                    print("** no instance found **")
                else:
                    del storage.all()[instKey]
                    storage.save()

    def do_all(self, ln):
        """Prints all string representation of all instances.
        """
        if ln != "":
            wrd = ln.split(' ')
            if wrd[0] not in storage.classes():
                print("** class doesn't exist **")
            else:
                instList = [str(obj) for key, obj in storage.all().items()
                            if type(obj).__name__ == wrd[0]]
                print(instList)
        else:
            all_instances = [str(obj) for key, obj in storage.all().items()]
            print(all_instances)

    def do_count(self, ln):
        """Counts the instances of a class.
        """
        wrd = ln.split(' ')
        if not wrd[0]:
            print("** class name missing **")
        elif wrd[0] not in storage.classes():
            print("** class doesn't exist **")
        else:
            instmche = [
                key for key in storage.all() if key.startswith(
                    wrd[0] + '.')]
            print(len(instmche))

    def do_update(self, ln):
        """Updates an instance by adding or updating attr.
        """
        if ln == "" or ln is None:
            print("** class name missing **")
            return

        rex = r'^(\S+)(?:\s(\S+)(?:\s(\S+)(?:\s((?:"[^"]*")|(?:(\S)+)))?)?)?'
        mch = re.search(rex, ln)
        cName = mch.group(1)
        instID = mch.group(2)
        attr = mch.group(3)
        value = mch.group(4)
        if not mch:
            print("** class name missing **")
        elif cName not in storage.classes():
            print("** class doesn't exist **")
        elif instID is None:
            print("** instance id missing **")
        else:
            instKey = "{}.{}".format(cName, instID)
            if instKey not in storage.all():
                print("** no instance found **")
            elif not attr:
                print("** attr name missing **")
            elif not value:
                print("** value missing **")
            else:
                cast = None
                if not re.search('^".*"$', value):
                    if '.' in value:
                        cast = float
                    else:
                        cast = int
                else:
                    value = value.replace('"', '')
                attrs = storage.attrs()[cName]
                if attr in attrs:
                    value = attrs[attr](value)
                elif cast:
                    try:
                        value = cast(value)
                    except ValueError:
                        pass  # fine, stay a string then
                setattr(storage.all()[instKey], attr, value)
                storage.all()[instKey].save()


if __name__ == '__main__':
    HBNBCommand().cmdloop()
