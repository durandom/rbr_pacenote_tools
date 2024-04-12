import configparser
import io
import logging
import os
from typing import Iterable

class IniFile:
    def __init__(self, file_path, parent=None):
        file_path = file_path.replace('\\', '/')
        # make sure the ini_file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'Not found: {file_path}')
        self.path = file_path
        self.base_dir = os.path.dirname(file_path)
        self.dir_name = os.path.basename(self.base_dir)
        self.file_name = os.path.basename(file_path)
        self.sections = {}

        self.parent = parent

        # logging.debug(f'IniFile: {file_path}')

        self.config = self.config_parser(file_path)
        self.parse()

    def __str__(self) -> str:
        return f'{self.file_name}'

    def config_parser(self, file):
        config = configparser.ConfigParser(strict=False)
        # https://stackoverflow.com/questions/19359556/configparser-reads-capital-keys-and-make-them-lower-case
        config.optionxform = str

        try:
            config.read(file, encoding='utf-8')
        except Exception as e:
            # logging.error(f'Error reading {file}: {e}')
            # work around for configparser not handling utf-8
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            # remove the BOM
            content = content.replace('\ufeff', '')
            config.read_string(content)
        return config

    def parse(self):
        pass

    def content(self):
        with io.StringIO() as ss:
            self.config.write(ss)
            ss.seek(0) # rewind
            return ss.read()

    def file_path(self, file):
        return os.path.join(self.base_dir, file)

class IniSection():
    def __init__(self, section, ini):
        self.section = section
        self._ini = ini
        self._config = ini.config
        self.options = self._config.options(section)
        self.entries = {}
        self.parse()

    def parse(self):
        pass

    def file_path(self, file):
        return self._ini.file_path(file)

    def ini(self):
        return self._ini

    def ini_tree(self):
        ini_file = self.ini()
        path = [ini_file]

        while ini_file.parent:
            ini_file = ini_file.parent.ini()
            path.append(ini_file)

        path.reverse()
        return path

class PluginIni(IniFile):
    def parse(self):
        pass
        # self.sounds_dir = self.config['SETTINGS'].get('sounds')
        # # check ig sounds is a valid directory
        # if not os.path.exists(self.sounds_dir):
        #     raise FileNotFoundError(f'Not found: {self.sounds_dir}')

    def language(self):
        return self.config['SETTINGS'].get('language')

class PackagesIni(IniFile):
    def parse(self):
        for section in self.config.sections():
            if section.startswith('PACKAGE'):
                self.sections[section] = Package(section, self)
            else:
                raise ValueError(f'Invalid section: {section}')

    def packages(self):
        return self.sections.values()

class Package(IniSection):
    def parse(self):
        (_type, name) = self.section.split('::')
        for option in self.options:
            if option.startswith('file'):
                file = self._config.get(self.section, option)
                file_path = self.file_path(file)
                self.entries[option] = CategoriesIni(file_path, parent=self)
            else:
                raise ValueError(f'Invalid option: {option}')

    def categories(self):
        for categories_ini in self.entries.values():
            for category in categories_ini.categories():
                yield category

class CategoriesIni(IniFile):
    def parse(self):
        for section in self.config.sections():
            if section.startswith('CATEGORY'):
                self.sections[section] = Category(section, self)
            else:
                raise ValueError(f'Invalid section: {section}')

    def categories(self):
        return self.sections.values()

class Category(IniSection):
    def parse(self):
        (_type, name) = self.section.split('::')
        for option in self.options:
            if option.startswith('file'):
                file = self._config.get(self.section, option)
                file_path = self.file_path(file)
                self.entries[option] = PacenotesIni(file_path, parent=self)
            else:
                raise ValueError(f'Invalid option: {option}')

    def pacenotes(self):
        for pacenotes_ini in self.entries.values():
            for pacenote in pacenotes_ini.pacenotes():
                yield pacenote

class PacenotesIni(IniFile):
    def parse(self):
        for section in self.config.sections():
            if section.startswith('PACENOTE'):
                self.sections[section] = Pacenote(section, self)
            elif section.startswith('RANGE'):
                self.sections[section] = Range(section, self)
            else:
                raise ValueError(f'Invalid section: {section}')

    def pacenotes(self):
        for pacenote in self.sections.values():
            yield pacenote

class Pacenote(IniSection):
    def parse(self):
        (_type, self._name) = self.section.split('::')
        for option in self.options:
            value = self._config.get(self.section, option)
            self.entries[option] = value

    def __str__(self):
        return f'{self.section} - {self.entries}'

    def id(self):
        _id = self.entries.get('id', None)
        if _id is None:
            return -1
        return int(_id)

    def name(self):
        return self._name

    def sounds(self):
        return int(self.entries.get('Sounds', 0))

    def files(self):
        _files = []
        for option in self.options:
            if option.startswith('Snd'):
                _files.append(self.entries[option])
        return _files

class Range(Pacenote):
    pass

class StringsIni(IniFile):
    def parse(self):
        self.strings = {}

        for section in self.config.sections():
            if section == 'STRINGS':
                for option in self.config.options(section):
                    translation = self.config.get(section, option)
                    self.strings[option] = translation
            else:
                raise ValueError(f'Invalid section: {section}')


class RbrPacenotePlugin:
    def __init__(self, dir = "Pacenote/",
                 ini_files = ["Rbr.ini", "Rbr-Enhanced.ini"]):
        self.plugin_dir = os.path.join(dir, 'Plugins', 'Pacenote')

        # make sure the plugin_dir is a directory
        if not os.path.isdir(self.plugin_dir):
            raise NotADirectoryError(f'Not a directory: {self.plugin_dir}')

        ini_file = os.path.join(self.plugin_dir, 'PaceNote.ini')
        self.pacenote_ini = PluginIni(ini_file)

        self.packages_ini = []
        for ini_file in ini_files:
            ini_file = os.path.join(self.plugin_dir, 'config', 'pacenotes', ini_file)
            self.packages_ini.append(PackagesIni(ini_file))

        # add ranges
        ini_file = os.path.join(self.plugin_dir, 'config', 'ranges', 'Rbr.ini')
        self.packages_ini.append(PackagesIni(ini_file))

        language_dir = os.path.join(self.plugin_dir, 'language')
        self.languages = {}
        # for each language in the language directory
        for language in os.listdir(language_dir):
            language_dir = os.path.join(self.plugin_dir, 'language', language)
            # recursively search for ini files in the pacenotes directory
            self.languages[language] = []
            for root, dirs, files in os.walk(os.path.join(language_dir, 'pacenotes')):
                for file in files:
                    if file.endswith('.ini'):
                        ini_file = os.path.join(root, file)
                        self.languages[language].append(StringsIni(ini_file))


    def pacenotes(self) -> Iterable[Pacenote]:
        for package_ini in self.packages_ini:
            for package in package_ini.packages():
                for category in package.categories():
                    for pacenote in category.pacenotes():
                        yield pacenote

    def translate(self, name, language=None):
        if not language:
            language = self.pacenote_ini.language()

        if language not in self.languages:
            raise ValueError(f'Invalid language: {language}')

        for strings_ini in self.languages[language]:
            if name in strings_ini.strings:
                return strings_ini.strings[name]
        return ''

    def add_translation(self, note):
        # ; So, if the plugin searches for a string to translate, e.g. ONE_LEFT
        # ; initially defined in the "cat1.ini" file in the "packages/category1"
        # ; directory, it searches for a file with an identical name, "cat1.ini", in
        # ; the parallel folder located beneath the language specific directory.
        # ; If that file is not found, the "strings.ini" in that same directory is
        # ; searched.
        # ; If none applies, the search continues one level above the current folder.
        # ; Again, the search starts with the original file name ("cat1.ini").
        # ; And so on, until the top-level directory has been reached.
        # ;
        # ; Note:
        # ; The translation should only be defined in one file, preferably in the
        # ; category specific file ("cat1.ini"). The strings.ini file serves as an
        # ; alternative or for convenience.
        # ; The above structure should be seen as an example. No need to create all
        # ; those files.
        files = [
            os.path.join('pacenotes', 'packages', note.category.lower(), f'{note.ini}'),
            os.path.join('pacenotes', 'packages', note.category.lower(), 'strings.ini'),
            os.path.join('pacenotes', 'packages', 'strings.ini'),
            os.path.join('pacenotes', 'strings.ini'),
        ]
        for file in files:
            file = os.path.join(self.plugin_dir, 'language', self.language, file)
            strings = self.strings(file)
            if strings and note.name in strings:
                note.translation = strings[note.name]
                # logging.debug(f'Translation: {note.name} -> {note.translation}')
                return

        if not note.translation:
            if note.name.isnumeric():
                note.translation = note.name
            else:
                logging.error(f'No translation for: {note.name}')
            # exit(1)
        # logging.debug(f'add_translation: {note}')

    def strings(self, file):
        if not os.path.exists(file):
            # logging.debug(f'Not found: {file}')
            return

        config = configparser.ConfigParser(strict=False)
        try:
            config.read(file, encoding='utf-8')
        except Exception as e:
            # logging.error(f'Error reading {file}: {e}')
            # work around for configparser not handling utf-8
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            # remove the BOM
            content = content.replace('\ufeff', '')
            config.read_string(content)

        strings = {}
        for section in config.sections():
            if section == 'STRINGS':
                for english in config.options(section):
                    # logging.debug(f'{english} - {config.get(section, english)}')
                    translation = config.get(section, english, fallback=None)
                    if translation:
                        strings[english] = translation.strip()
        return strings



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.ERROR)
    basedir = os.path.dirname(os.path.abspath(__file__))
    pacenote_dir = os.path.join(basedir, "Pacenote")
    logging.debug(f'ini_file: {pacenote_dir}')
    rbr_pacenote_plugin = RbrPacenotePlugin(pacenote_dir)