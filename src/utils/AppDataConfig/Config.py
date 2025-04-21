# FlippyFlappingTheJ
# ./src/utils/AppDataConfig/Config.py

import json


class ConfigurationFile:

    __slots__ = ("url", "data")

    def __init__(self, fp):

        self.url = fp

        with open(r'%s' % self.url, "r") as read_file:
            self.data = json.load(read_file)

    def __str__(self):
        return f"ConfigurationFile: {self.url}"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        return self.getValue(key)

    def __setitem__(self, key, value):
        self.setValue(key, value)

    def getPath(self):
        return self.url

    def getConfigurationSection(self, name):
        return ConfigurationSection(self.url, self.data[name])

    def getValue(self, path):
        try:
            section = self.data
            if str(path).__contains__("."):
                sp = str(path).split(".")
                for i in range(len(sp)):
                    if i == len(sp) - 1:
                        if isinstance(section[sp[i]], dict) or isinstance(section[sp[i]], list):
                            return ConfigurationSection(self.url, section[sp[i]])
                        else:
                            return section[sp[i]]
                    section = section[sp[i]]
            else:
                return section[path]
        except KeyError:
            return False

    def _set_value_recursion(self, sec, split, val):
        if len(split) > 1:
            cur = split[1:]
            sec = self._set_value_recursion(sec[split[0]], cur, val)
        else:
            sec[split[0]] = val
        return sec

    def setValue(self, path, value):

        if str(path).__contains__("."):
            sp = str(path).split(".")
            self._set_value_recursion(self.data, sp, value)
            with open(self.url, "w") as write_file:
                write_file.write(json.dumps(self.data))
        else:
            self.data[path] = value
            with open(r'%s' % self.url, "w") as write_file:
                write_file.write(json.dumps(self.data, indent=4, sort_keys=True, separators=(',', ': ')).replace("\\n", "\n"))


class ConfigurationSection(object):

    __slots__ = ("url", "section")

    def __init__(self, fp, section):

        self.section = section
        self.url = fp

    @staticmethod
    def getSectionFromFile(fp, key):
        file = ConfigurationFile(fp)
        return file.getConfigurationSection(key)

    def __str__(self):
        return f"ConfigurationSection: {self.url}, {self.section}"

    def __repr__(self):
        return self.__str__()

    def __getitem__(self, key):
        return self.getValue(key)

    def __setitem__(self, key, value):
        self.setValue(key, value)

    def getCurrentSection(self):
        return self.section

    def getConfigurationSection(self, name):
        return ConfigurationSection(self.url, self.section[name])

    def getValue(self, path):
        try:
            section = self.section
            if str(path).__contains__("."):
                sp = str(path).split(".")
                for i in range(len(sp)):
                    if i == len(sp) - 1:
                        if isinstance(section[sp], dict) or isinstance(section[sp], list):
                            return ConfigurationSection(self.url, section[sp])
                        else:
                            return section[sp]
                    section = section[sp]
            else:
                return section[path]
        except KeyError:
            return False

    def _set_value_recursion(self, sec, split, val):
        if len(split) > 1:
            cur = split[1:]
            sec = self._set_value_recursion(sec[split[0]], cur, val)
        else:
            sec[split[0]] = val
        return sec

    def setValue(self, path, value):

        if str(path).__contains__("."):
            sp = str(path).split(".")
            self._set_value_recursion(self.section, sp, value)
            with open(self.url, "w") as write_file:
                write_file.write(json.dumps(self.section))
        else:
            self.section[path] = value
            with open(r'%s' % self.url, "w") as write_file:
                write_file.write(json.dumps(self.section, indent=4, sort_keys=True, separators=(',', ': ')).replace("\\n", "\n"))
