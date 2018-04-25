import io
import struct
from polyglot_detector.polyglot_level import PolyglotLevel
from polyglot_detector.utils import must_read

FILE_EXTENSION = 'png'

RULES = """
rule IsPNG {
  strings:
    $magic = { 89 50 4E 47 0D 0A 1A 0A }
    
  condition:
    $magic at 0
}
"""

_MAGIC = b'\x89PNG\r\n\x1a\n'
_CRC_SIZE = 4
_PNG_SECTION_HEADING_SIZE = 8
_PNG_END_SECTION = 'IEND'


def check_with_matches(filename, matches):
    if 'IsPNG' in matches:
        return check(filename)
    return None


def check(filename: str):

    with open(filename, 'rb') as file:
        if file.read(len(_MAGIC)) != _MAGIC:
            return None
        try:
            name = ''
            while name != _PNG_END_SECTION:
                name, length = read_section(file)
                file.seek(length + _CRC_SIZE, io.SEEK_CUR)
            file.seek(_CRC_SIZE, io.SEEK_CUR)
            flag = PolyglotLevel.VALID
            if len(file.read(1)) != 0:
                flag |= PolyglotLevel.GARBAGE_AT_END
            return flag
        except SyntaxError:
            return None


def read_section(file) -> (str, int):
    section_heading = must_read(file, _PNG_SECTION_HEADING_SIZE)
    name = section_heading[4:].decode('utf-8')
    length = struct.unpack('>I', section_heading[:4])[0]
    return name, length
