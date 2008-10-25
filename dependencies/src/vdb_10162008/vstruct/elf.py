"""
Elf structure definitions
"""

from vstruct import VStruct,VArray
from vstruct.primitives import *

class Elf32Symbol(VStruct):
    _fields_ =  [
        ("st_name", v_uint32),
        ("st_value", v_uint32),
        ("st_size", v_uint32),
        ("st_info", v_uint8),
        ("st_other", v_uint8),
        ("st_shndx", v_uint16)
    ]

class Elf32Reloc(VStruct):
    _fields_ = [
        ("r_offset", v_ptr),
        ("r_info", v_uint32),
    ]

    def getType(self):
        return int(self.r_info) & 0xff

    def getSymTabIndex(self):
        return int(self.r_info) >> 8

class Elf32Dynamic(VStruct):
    _fields_ = [
        ("d_tag", v_uint32),
        ("d_value", v_uint32),
    ]

class Elf64Symbol(VStruct):
    pass

class ElfIdent(v_base_t):
    _fmt_ = "16s"
    def __repr__(self):
        return self.value.encode("hex")

class Elf32(VStruct):
    _fields_ = [
        ("e_ident", ElfIdent),
        ("e_type", v_uint16),
        ("e_machine", v_uint16),
        ("e_version", v_uint32),
        ("e_entry", v_uint32),
        ("e_phoff", v_uint32),
        ("e_shoff", v_uint32),
        ("e_flags", v_uint32),
        ("e_ehsize", v_uint16),
        ("e_phentsize", v_uint16),
        ("e_phnum", v_uint16),
        ("e_shentsize", v_uint16),
        ("e_shnum", v_uint16),
        ("e_shstrndx", v_uint16),
    ]

