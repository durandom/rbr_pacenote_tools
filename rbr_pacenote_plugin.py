from configobj import ConfigObj, ConfigObjError
import re
from io import StringIO
import io
import logging
import os
from pathlib import Path
from typing import Iterable, List, Tuple, Union

class IniFile:
    def __init__(self, pathname, parent=None):
        pathname = pathname.replace('\\', '/')
        # make sure the ini_file exists
        if not os.path.exists(pathname):
            raise FileNotFoundError(f'Not found: {pathname}')
        # /path/to/file.ini
        self.pathname = pathname
        # /path/to
        self.dirname = os.path.dirname(pathname)
        # to
        self.basename = os.path.basename(self.dirname)
        # file.ini
        self.filename = os.path.basename(pathname)
        self.sections = {}

        self.parent = parent

        # logging.debug(f'IniFile: {file_path}')

        self.duplicate_sections = {}

        self.config = self.config_parser(pathname)
        self.parse()

    def __str__(self) -> str:
        return f'{self.filename}'

    def parse(self):
        pass

    def config_parser(self, file):
        try:
            with open(file, 'r', encoding='utf-8') as file:
                # strip bom
                file_contents = file.read()
                file_contents = file_contents.replace('\ufeff', '')

                # Corrects ";" at the start of any line to "#" throughout the file.
                # file_contents = re.sub(r'^\s*;', '#', file_contents, flags=re.MULTILINE)
                file_contents = re.sub(r';', '#', file_contents, flags=re.MULTILINE)

            # Use StringIO to simulate a file object with the modified contents.
            file_contents = StringIO(file_contents)
            file_contents = file_contents.readlines()

            # Dictionary to count occurrences of sections
            sections = {}
            processed_lines = []
            for line in file_contents:
                if line.startswith('['):
                    new_line = line
                    section = new_line.strip().strip('[]')
                    if section in sections:
                        sections[section] += 1
                        new_section = f"{section}_{sections[section]}"
                        processed_lines.append(f"[{new_section}]\n")
                        self.duplicate_sections[new_section] = section
                    else:
                        sections[section] = 0
                        processed_lines.append(line)
                else:
                    processed_lines.append(line)

            # Write the processed content to a temporary file or handle in-memory
            processed_content = ''.join(processed_lines)

            # Use StringIO to simulate a file object with the modified contents.
            string_io = StringIO(processed_content)
            config = ConfigObj(string_io, encoding='utf-8', file_error=True)
        except ConfigObjError as e:
            logging.error('Parsing failed with several errors:')
            for error in e.errors:
                logging.error(f'Error: {error}')
            exit(1)  # Or handle the error in a way that suits your application's needs
        except IOError as e:
            # This handles cases where the file might not be accessible or found
            logging.error(f'I/O error({e.errno}): {e.strerror}')
            exit(1)
        return config

    def content(self):
        content = self.config.write()
        # Decode each byte string to a regular string (assuming UTF-8 encoding)
        decoded_strings = [byte.decode('utf-8') for byte in content]
        # replace # by ;
        decoded_strings = [re.sub(r'#', ';', line) for line in decoded_strings]
        # replace " = " by "="
        decoded_strings = [re.sub(r' = ', '=', line) for line in decoded_strings]
        # undo the duplicate sections
        strings = []
        for line in decoded_strings:
            for new_section, orig_section in self.duplicate_sections.items():
                if f"[{new_section}]" in line:
                    line = line.replace(f"[{new_section}]", f"[{orig_section}]")
            strings.append(line)

        return "\n".join(strings)

    def get_options(self, section):
        return self.config[section].keys()

    def get_option(self, section, option):
        return self.config[section][option]

    def file_path(self, file):
        return os.path.join(self.dirname, file)

class IniSection():
    ini_files = {}
    def __init__(self, section, ini):
        self.section = section
        self._ini = ini
        self.entries = {}
        self.parse()

    def parse(self):
        pass

    def get_ini_file(self, file_path, parent=None, klass=None):
        if not klass:
            klass = IniFile

        if file_path in self.ini_files:
            return self.ini_files[file_path]

        self.ini_files[file_path] = klass(file_path, parent=parent)
        return self.ini_files[file_path]

    def options(self):
        return self._ini.get_options(self.section)

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
        return self.get_option('SETTINGS', 'language')

class PackagesIni(IniFile):
    def parse(self):
        for section in self.config.sections:
            if section.startswith('PACKAGE'):
                self.sections[section] = Package(section, self)
            else:
                raise ValueError(f'Invalid section: {section}')

    def packages(self):
        return self.sections.values()

class Package(IniSection):
    def parse(self):
        (_type, name) = self.section.split('::')
        for option in self.options():
            if option.startswith('file'):
                file = self._ini.get_option(self.section, option)
                file_path = self.file_path(file)
                self.entries[option] = self.get_ini_file(file_path, parent=self, klass=CategoriesIni)
            else:
                raise ValueError(f'Invalid option: {option}')

    def categories(self):
        for categories_ini in self.entries.values():
            for category in categories_ini.categories():
                yield category

class CategoriesIni(IniFile):
    def parse(self):
        for section in self.config.sections:
            if section.startswith('CATEGORY'):
                self.sections[section] = Category(section, self)
            else:
                raise ValueError(f'Invalid section: {section}')

    def categories(self):
        return self.sections.values()

class Category(IniSection):
    def parse(self):
        (_type, name) = self.section.split('::')
        for option in self.options():
            if option.startswith('file'):
                file = self._ini.get_option(self.section, option)
                file_path = self.file_path(file)
                self.entries[option] = self.get_ini_file(file_path, parent=self, klass=PacenotesIni)
            else:
                raise ValueError(f'Invalid option: {option}')

    def pacenotes(self):
        for pacenotes_ini in self.entries.values():
            for pacenote in pacenotes_ini.pacenotes():
                yield pacenote

class PacenotesIni(IniFile):
    def parse(self):
        for section in self.config.sections:
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
        # for option in self.options():
        #     value = self._config.get(self.section, option)
        #     self.entries[option] = value

    def __str__(self):
        return f'{self.section} - {self.entries}'

    def get(self, key, default=None):
        return self._config[self.section].dict().get(key, default)

    def id(self):
        _id = self.get('id', None)
        if _id is None:
            return -1
        return int(_id)

    def name(self):
        return self._name

    def sounds(self):
        # return int(self.entries.get('Sounds', 0))
        sounds = self.get('Sounds', 0)
        return int(sounds)

    def files(self):
        _files = []
        for option in self.options():
            if option.startswith('Snd'):
                file = self.get(option)
                _files.append(file)
        return _files

    def merge_queue(self, note):
        if not hasattr(self, 'queue'):
            self.queue = []
        # only add the note if it is not already in the queue
        if note['file'] not in [n['file'] for n in self.queue]:
            self.queue.append(note)

    def merge_commit(self):
        if hasattr(self, 'queue'):
            # remove all Snd options
            for option in self.options():
                if option.startswith('Snd'):
                    del self._config[self.section][option]

            # iterate over queue with index
            for idx, note in enumerate(self.queue):
                # add Snd options
                option = f'Snd{idx}'
                file = note['file']
                self._config[self.section][option] = file

            self._config[self.section]['Sounds'] = str(len(self.queue))

class Range(Pacenote):
    pass

class StringsIni(IniFile):
    def parse(self):
        self.strings = {}

        for section in self.config.sections:
            if section == 'STRINGS':
                for option in self.config[section].keys():
                    translation = self.config[section][option]
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

        self.inifiles = []

        ini_file = os.path.join(self.plugin_dir, 'PaceNote.ini')
        self.pacenote_ini = PluginIni(ini_file)
        self.inifiles.append(self.pacenote_ini)

        self.packages_ini = []
        for ini_file in ini_files:
            ini_file = os.path.join(self.plugin_dir, 'config', 'pacenotes', ini_file)
            self.packages_ini.append(PackagesIni(ini_file))

        # add ranges
        ini_file = os.path.join(self.plugin_dir, 'config', 'ranges', 'Rbr.ini')
        self.packages_ini.append(PackagesIni(ini_file))
        ini_file = os.path.join(self.plugin_dir, 'config', 'ranges', 'Extended.ini')
        self.packages_ini.append(PackagesIni(ini_file))

        ini_file = os.path.join(self.plugin_dir, 'config', 'ranges', 'packages', 'Rbr.ini')
        self.inifiles.append(CategoriesIni(ini_file))

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

    def write_ini(self, ini_file, basedir):
        dir = Path(ini_file.dirname).relative_to(self.plugin_dir)
        out_dir = os.path.join(basedir, dir)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(os.path.join(out_dir, ini_file.filename), 'w', encoding='utf-8') as f:
            f.write(ini_file.content())

    def get_linked_inis(self, ini):
        linked_inis = []
        for section in ini.sections.values():
            for entry in section.entries.values():
                linked_inis.append(entry)
                for linked_ini in self.get_linked_inis(entry):
                    linked_inis.append(linked_ini)
        return linked_inis

    def write(self, out_path):
        basedir = os.path.join(out_path, 'Plugins', 'Pacenote')
        inis = []
        for ini in self.packages_ini + self.inifiles:
            inis.append(ini)
            for linked_ini in self.get_linked_inis(ini):
                if linked_ini not in inis:
                    inis.append(linked_ini)
                    self.write_ini(linked_ini, basedir)

        for language, strings_ini in self.languages.items():
            for strings in strings_ini:
                self.write_ini(strings, basedir)


    def pacenotes(self, with_ini_tree = False) -> Iterable[Union[Pacenote, Tuple[Pacenote, List[IniFile]]]]:
        for package_ini in self.packages_ini:
            ini_tree = [ package_ini, None, None ]
            for package in package_ini.packages():
                for category_ini in package.entries.values():
                    ini_tree[1] = category_ini
                    for category in category_ini.categories():
                        for pacenotes_ini in category.entries.values():
                            ini_tree[2] = pacenotes_ini
                            for pacenote in pacenotes_ini.pacenotes():
                                if with_ini_tree:
                                    yield pacenote, ini_tree
                                else:
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

    def merge(self, note):
        id = int(note['id'])
        pacenotes = self.find_pacenotes(id, note['name'])
        for pacenote in pacenotes:
            pacenote.merge_queue(note)

    def merge_commit(self):
        for pacenote in self.pacenotes():
            pacenote.merge_commit()

    def find_pacenotes(self, id, name):
        notes = []
        for pacenote in self.pacenotes():
            if id == -1 and pacenote.name() == name:
                notes.append(pacenote)
            elif id != -1 and pacenote.id() == id:
                notes.append(pacenote)
        return notes

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

        config = ConfigObj(file, encoding='utf-8')
        strings = {}
        for section in config.sections:
            if section == 'STRINGS':
                for english in config[section].keys():
                    # logging.debug(f'{english} - {config.get(section, english)}')
                    translation = config[section][english]
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
