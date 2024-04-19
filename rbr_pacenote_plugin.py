import shutil
from configobj import ConfigObj, ConfigObjError
import re
from io import StringIO
import logging
import os
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple, Union

class IniFile:
    def __init__(self, pathname, plugin: "RbrPacenotePlugin"):
        self.plugin = plugin
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
        # dict of section_name -> IniSection
        self.sections : Dict[str, IniSection] = {}

        # logging.debug(f'IniFile: {file_path}')

        self.duplicate_sections = {}

        self.config = self.config_parser(pathname)
        self.parse()

    def __str__(self) -> str:
        return f'{self.filename}'

    def __repr__(self) -> str:
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

    def get_options(self, section) -> List[str]:
        return self.config[section].keys()

    def get_option(self, section: str, option: str) -> Union[str, None]:
        try:
            return self.config[section][option]
        except KeyError:
            return None

    def get_sections(self) -> List[str]:
        return self.config.sections

    def get_ini_sections(self) -> List["IniSection"]:
        return list(self.sections.values())

    def add_ini_section(self, section: str, ini_section: "IniSection"):
        self.sections[section] = ini_section

    def file_path(self, file):
        return os.path.join(self.dirname, file)

class IniSection():
    ini_files : Dict[str, IniFile] = {}
    def __init__(self, name, ini):
        self._name = name
        self._ini: IniFile = ini
        self.options: Dict[str, str] = {}
        self._linked_inis: Dict[str, IniFile] = {}
        self.parse()

    def __str__(self) -> str:
        return f'{self._name}'

    def __repr__(self) -> str:
        return f'{self._name}'

    def error(self):
        return ''

    def file_error(self, file):
        return ''

    def parse(self):
        pass

    def get_ini_file(self, file_path, klass=None):
        if not klass:
            klass = IniFile

        if file_path in self.ini_files:
            ini_file = self.ini_files[file_path]
        else:
            ini_file = klass(file_path, self._ini.plugin)
            self.ini_files[file_path] = ini_file

        self._linked_inis[file_path] = ini_file

        return ini_file

    def get_linked_inis(self) -> List[IniFile]:
        return list(self._linked_inis.values())

    def get_options(self) -> List[str]:
        return self._ini.get_options(self._name)

    def get_option(self, option, default = None) -> Union[str, None]:
        value = self._ini.get_option(self._name, option)
        if value is None:
            return default
        else:
            return value

    def del_option(self, option):
        del self._ini.config[self._name][option]

    def add_option(self, option, value):
        self._ini.config[self._name][option] = value

    def set_option(self, option, value):
        self._ini.config[self._name][option] = value

    def file_path(self, file):
        return self._ini.file_path(file)

    def ini(self):
        return self._ini

    def plugin(self):
        return self._ini.plugin

class PluginIni(IniFile):
    def parse(self):
        pass
        # self.sounds_dir = self.config['SETTINGS'].get('sounds')
        # # check ig sounds is a valid directory
        # if not os.path.exists(self.sounds_dir):
        #     raise FileNotFoundError(f'Not found: {self.sounds_dir}')

    def language(self) -> str:
        return str(self.get_option('SETTINGS', 'language'))

    def sounds(self) -> str:
        return str(self.get_option('SETTINGS', 'sounds'))

class PackagesIni(IniFile):
    def parse(self):
        for section in self.get_sections():
            if section.startswith('PACKAGE'):
                self.add_ini_section(section, Package(section, self))
            else:
                raise ValueError(f'Invalid section: {section}')

class Package(IniSection):
    def parse(self):
        for option in self.get_options():
            if option.startswith('file'):
                file = self.get_option(option)
                file_path = self.file_path(file)
                self.get_ini_file(file_path, klass=CategoriesIni)
            else:
                raise ValueError(f'Invalid option: {option}')

class CategoriesIni(IniFile):
    def parse(self):
        for section in self.get_sections():
            if section.startswith('CATEGORY'):
                self.add_ini_section(section, Category(section, self))
            else:
                raise ValueError(f'Invalid section: {section}')

class Category(IniSection):
    def parse(self):
        for option in self.get_options():
            if option.startswith('file'):
                file = self._ini.get_option(self._name, option)
                file_path = self.file_path(file)
                self.get_ini_file(file_path, klass=PacenotesIni)
            else:
                raise ValueError(f'Invalid option: {option}')

class PacenotesIni(IniFile):
    def parse(self):
        for section in self.get_sections():
            if section.startswith('PACENOTE'):
                self.add_ini_section(section, Pacenote(section, self))
            elif section.startswith('RANGE'):
                self.add_ini_section(section, Range(section, self))
            else:
                raise ValueError(f'Invalid section: {section}')

class Pacenote(IniSection):
    def __init__(self, name, ini):
        super().__init__(name, ini)
        self._sound_dir = None
        self._merge_queue = []

    def parse(self):
        pass
        # (_type, self._name) = self.name.split('::')
        # for option in self.options():
        #     value = self._config.get(self.section, option)
        #     self.entries[option] = value

    def id(self):
        _id = self.get_option('id', None)
        if _id is None:
            return -1
        return int(_id)

    def type(self):
        return self._name.split('::')[0]

    def name(self):
        if self._name in self._ini.duplicate_sections:
            return self._ini.duplicate_sections[self._name].split('::')[1]
        return self._name.split('::')[1]

    def sounds(self):
        # return int(self.entries.get('Sounds', 0))
        sounds = self.get_option('Sounds')
        if sounds is None:
            return 0
        return int(sounds)

    def get_sound_dir(self) -> Optional[Path]:
        return self._sound_dir

    def files(self) -> List[str]:
        _files = []
        for option in self.get_options():
            if option.startswith('Snd'):
                file = self.get_option(option)
                _files.append(file)
        return _files

    def file_error(self, file):
        if not file:
            # internal file
            return ''
        # if file does not have .ogg extension, add it
        if not file.endswith('.ogg'):
            file = f'{file}.ogg'
        # check if the file exists
        if self._sound_dir:
            pathname = os.path.join(self._sound_dir, file)
        else:
            pathname = self.plugin().pathname_for(self, file)
        if not os.path.exists(pathname):
            return f'Not found: {file}'
        return ''

    def merge_queue(self, note, sound_dir: Path):
        # only add the note if it is not already in the queue
        if note['file'] not in [n['file'] for n in self._merge_queue]:
            self._sound_dir = sound_dir
            self._merge_queue.append(note)

    def merge_commit(self):
        if self._merge_queue:
            # remove all Snd options
            for option in self.get_options():
                if option.startswith('Snd'):
                    self.del_option(option)

            # iterate over queue with index
            for idx, note in enumerate(self._merge_queue):
                # add Snd options
                option = f'Snd{idx}'
                file = note['file']
                self.add_option(option, file)

            # update the Sounds option
            self.set_option('Sounds', str(len(self._merge_queue)))

class Range(Pacenote):
    pass

class NumbersIni(IniFile):
    def parse(self):
        for section in self.get_sections():
            if section.startswith('PLACE'):
                self.add_ini_section(section, Place(section, self))
            elif section.startswith('NUMBER'):
                self.add_ini_section(section, Number(section, self))
            elif section.startswith('RANGE'):
                self.add_ini_section(section, Range(section, self))
            else:
                raise ValueError(f'Invalid section: {section}')

class Place(Pacenote):
    pass

class Number(Pacenote):
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
        self.dirname = dir
        self.root_ini_files = ini_files

        self.plugin_dir = os.path.join(dir, 'Plugins', 'Pacenote')
        self._merge_language = None

        # make sure the plugin_dir is a directory
        if not os.path.isdir(self.plugin_dir):
            raise NotADirectoryError(f'Not a directory: {self.plugin_dir}')

        self.inifiles: List[IniFile] = []

        ini_file = os.path.join(self.plugin_dir, 'PaceNote.ini')
        self.pacenote_ini = PluginIni(ini_file, self)
        self.inifiles.append(self.pacenote_ini)

        for ini_file in ini_files:
            ini_file = os.path.join(self.plugin_dir, 'config', 'pacenotes', ini_file)
            self.inifiles.append(PackagesIni(ini_file, self))

        # add ranges
        ini_file = os.path.join(self.plugin_dir, 'config', 'ranges', 'Rbr.ini')
        self.inifiles.append(PackagesIni(ini_file, self))
        ini_file = os.path.join(self.plugin_dir, 'config', 'ranges', 'Extended.ini')
        self.inifiles.append(PackagesIni(ini_file, self))

        ini_file = os.path.join(self.plugin_dir, 'config', 'ranges', 'packages', 'Rbr.ini')
        self.inifiles.append(CategoriesIni(ini_file, self))

        # add numbers
        ini_file = os.path.join(self.dirname, 'Audio', 'Numbers.ini')
        # check if the ini_file exists
        if os.path.exists(ini_file):
            self.inifiles.append(NumbersIni(ini_file, self))

        ini_file = os.path.join(self.dirname, 'Audio', 'NumOther.ini')
        # check if the ini_file exists
        if os.path.exists(ini_file):
            self.inifiles.append(NumbersIni(ini_file, self))

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
                        self.languages[language].append(StringsIni(ini_file, self))

    def copy(self):
        return RbrPacenotePlugin(dir=self.dirname, ini_files=self.root_ini_files)

    def write_ini(self, ini_file, basedir):
        dir = Path(ini_file.dirname).relative_to(self.dirname)
        out_dir = os.path.join(basedir, dir)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)
        with open(os.path.join(out_dir, ini_file.filename), 'w', encoding='utf-8') as f:
            f.write(ini_file.content())

    def get_linked_inis(self, ini):
        linked_inis = []
        for section in ini.sections.values():
            for ini_file in section.get_linked_inis():
                linked_inis.append(ini_file)
                for linked_ini in self.get_linked_inis(ini_file):
                    linked_inis.append(linked_ini)
        return linked_inis

    def pathname_for(self, call, file):
        language_to_dir = {
            'english': 'Number',
            'german': 'NumGer',
            'french': 'NumFre',
        }
        src_number_dir = language_to_dir[self.pacenote_ini.language()]

        src_dirs = {
            Pacenote: Path('Plugins', 'Pacenote', 'sounds', self.pacenote_ini.sounds()),
            Range: Path('Plugins', 'Pacenote', 'sounds', self.pacenote_ini.sounds()),
            Number: Path('Audio', 'Speech', src_number_dir),
            Place: Path('Audio', 'Speech', src_number_dir),
        }
        return os.path.join(self.dirname, src_dirs[type(call)], file)

    def write(self, out_path):
        inis = []
        for ini in self.inifiles:
            self.write_ini(ini, out_path)
            for linked_ini in self.get_linked_inis(ini):
                if linked_ini not in inis:
                    inis.append(linked_ini)
                    self.write_ini(linked_ini, out_path)

        for language, strings_ini in self.languages.items():
            for strings in strings_ini:
                self.write_ini(strings, out_path)

        language_to_dir = {
            'english': 'Number',
            'german': 'NumGer',
            'french': 'NumFre',
        }
        src_number_dir = language_to_dir[self.pacenote_ini.language()]
        dst_number_dir = language_to_dir[self.get_merge_language()]


        src_dirs = {
            Pacenote: Path('Plugins', 'Pacenote', 'sounds', self.pacenote_ini.sounds()),
            Range: Path('Plugins', 'Pacenote', 'sounds', self.pacenote_ini.sounds()),
            Number: Path('Audio', 'Speech', src_number_dir),
            Place: Path('Audio', 'Speech', src_number_dir),
        }
        dst_dirs = {
            Pacenote: Path('Plugins', 'Pacenote', 'sounds', self.pacenote_ini.sounds()),
            Range: Path('Plugins', 'Pacenote', 'sounds', self.pacenote_ini.sounds()),
            Number: Path('Audio', 'Speech', dst_number_dir),
            Place: Path('Audio', 'Speech', dst_number_dir),
        }

        for pacenote in self.pacenotes():
            for file in pacenote.files():
                if not file:
                    continue

                # check if file has .ogg extension, if not, add it
                if not file.endswith('.ogg'):
                    file = f'{file}.ogg'

                src_dir = pacenote.get_sound_dir()
                if not src_dir:
                    src_dir = os.path.join(self.dirname, src_dirs[type(pacenote)])
                dst_dir = os.path.join(out_path, dst_dirs[type(pacenote)])

                src = os.path.join(src_dir, file)
                dst = os.path.join(dst_dir, file)

                if not os.path.exists(src):
                    logging.error(f'Not found: {src}')
                else:
                    if not os.path.exists(dst_dir):
                        os.makedirs(dst_dir)
                    logging.debug(f'Copying: {src} -> {dst}')
                    shutil.copy(src, dst)

    def calls_with_ini_tree(self, ini = None, ini_tree = []) -> Iterable[Tuple[Pacenote, List[IniFile]]]:
        if not ini:
            for ini in self.inifiles:
                yield from self.calls_with_ini_tree(ini = ini)
        else:
            ini_tree.append(ini)
            for ini_section in ini.get_ini_sections():
                if issubclass(type(ini_section), Pacenote):
                    yield ini_section, ini_tree

            for linked_ini in self.get_linked_inis(ini):
                yield from self.calls_with_ini_tree(ini = linked_ini, ini_tree = ini_tree)
            ini_tree.pop()

    def pacenotes(self) -> Iterable[Pacenote]:
        for pacenote, _ini_tree in self.calls_with_ini_tree():
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

    def merge(self, note, sound_dir=None):
        id = int(note['id'])
        pacenotes = self.find_pacenotes(id, note['name'])
        for pacenote in pacenotes:
            pacenote.merge_queue(note, sound_dir)

    def merge_commit(self):
        for pacenote in self.pacenotes():
            pacenote.merge_commit()

    def merge_language(self, language):
        self._merge_language = language

    def get_merge_language(self):
        if not self._merge_language:
            return self.pacenote_ini.language()
        return self._merge_language

    def find_pacenotes(self, id, name) -> List[Pacenote]:
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