import struct
from io import BytesIO

class EndianBinaryFileReader:
    def __init__(self,filepath : str, endianness : str = 'little'):
        self.filepath = filepath
        self.set_endianness(endianness)

    def __enter__(self):
        self.file = open(self.filepath,mode='rb')
        self.read = self.file.read
        self.tell = self.file.tell
        self.seek = self.file.seek
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.file.close()

    def set_endianness(self, endianness : str):
        if endianness == 'little':
            self.endian_flag = '<'
        elif endianness == 'big':
            self.endian_flag = '>'
        else:
            raise Exception(r"Unknown endianness : should be 'little' or 'big'")

    def read_Int8(self) -> int:
        return struct.unpack(f'{self.endian_flag}b',self.read(1))[0]

    def read_UInt8(self) -> int:
        return struct.unpack(f'{self.endian_flag}B',self.read(1))[0]

    def read_Int16(self) -> int:
        return struct.unpack(f'{self.endian_flag}h',self.read(2))[0]
    
    def read_UInt16(self) -> int:
        return struct.unpack(f'{self.endian_flag}H',self.read(2))[0]

    def read_Int32(self) -> int:
        return struct.unpack(f'{self.endian_flag}i',self.read(4))[0]
    
    def read_UInt32(self) -> int:
        return struct.unpack(f'{self.endian_flag}I',self.read(4))[0]

    def read_Int64(self) -> int:
        return struct.unpack(f'{self.endian_flag}q',self.read(8))[0]
    
    def read_UInt64(self) -> int:
        return struct.unpack(f'{self.endian_flag}Q',self.read(8))[0]

    def read_string(self, encoding : str, size : int) -> str:
        return self.read(size).decode(encoding)
    
    def read_string_until_null(self, encoding : str) -> str:
        data = b""
        byte = self.read(1)
        while byte not in [b"\x00", b""]:
            data += byte
            byte = self.read(1)
        assert byte != b"", "EOF reached"
        return data.decode(encoding)
    
    def read_utf16_until_null(self) -> str:
        data = b""
        charbytes = self.read(2)
        while charbytes not in [b"\x00\x00", b""]:
            data += charbytes
            charbytes = self.read(2)
        assert charbytes != b"", "EOF reached"
        return data.decode("utf-16")

    def align(self, alignment : int):
        mod = self.tell() % alignment
        if mod != 0:
            self.read(alignment - mod)

class EndianBinaryStreamReader:
    def __init__(self,stream : bytes, endianness : str = 'little'):
        self.set_endianness(endianness)
        self.stream = BytesIO(stream)
        self.read = self.stream.read
        self.tell = self.stream.tell
        self.seek = self.stream.seek
        self.getvalue = self.stream.getvalue

    def set_endianness(self, endianness : str):
        if endianness == 'little':
            self.endian_flag = '<'
        elif endianness == 'big':
            self.endian_flag = '>'
        else:
            raise Exception(r"Unknown endianness : should be 'little' or 'big'")

    def read_Int8(self) -> int:
        return struct.unpack(f'{self.endian_flag}b',self.read(1))[0]

    def read_UInt8(self) -> int:
        return struct.unpack(f'{self.endian_flag}B',self.read(1))[0]

    def read_Int16(self) -> int:
        return struct.unpack(f'{self.endian_flag}h',self.read(2))[0]
    
    def read_UInt16(self) -> int:
        return struct.unpack(f'{self.endian_flag}H',self.read(2))[0]

    def read_Int32(self) -> int:
        return struct.unpack(f'{self.endian_flag}i',self.read(4))[0]
    
    def read_UInt32(self) -> int:
        return struct.unpack(f'{self.endian_flag}I',self.read(4))[0]

    def read_Int64(self) -> int:
        return struct.unpack(f'{self.endian_flag}q',self.read(8))[0]
    
    def read_UInt64(self) -> int:
        return struct.unpack(f'{self.endian_flag}Q',self.read(8))[0]

    def read_string(self, encoding : str, size : int) -> str:
        return self.read(size).decode(encoding)
    
    def read_utf16_until_null(self) -> str:
        output = ""
        char = self.read(2).decode('utf-16')
        while char not in ["\x00", ""]:
            output += char
            char = self.read(2).decode('utf-16')
        assert char != ""
        return output

    def align(self, alignment : int):
        mod = self.tell() % alignment
        if mod != 0:
            self.read(alignment - mod)