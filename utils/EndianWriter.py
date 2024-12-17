import struct

class EndianBinaryFileWriter:
    def __init__(self,filepath : str, endianness : str = 'little'):
        self.filepath = filepath
        self.set_endianness(endianness)

    def __enter__(self):
        self.file = open(self.filepath,mode='wb')
        self.write = self.file.write
        self.tell = self.file.tell
        self.seek = self.file.seek
        return self

    def __exit__(self,exc_type, exc_val, exc_tb):
        self.file.close()

    def set_endianness(self, endianness : str):
        if endianness == 'little':
            self.endian_flag = '<'
        elif endianness == 'big':
            self.endian_flag = '>'
        else:
            raise Exception(r"Unknown endianness : should be 'little' or 'big'")

    def write_Int8(self,value: int):
        self.file.write(struct.pack(f'{self.endian_flag}b',value))

    def write_UInt8(self,value: int):
        self.file.write(struct.pack(f'{self.endian_flag}B',value))

    def write_Int16(self,value: int):
        self.file.write(struct.pack(f'{self.endian_flag}h',value))
    
    def write_UInt16(self,value: int):
        self.file.write(struct.pack(f'{self.endian_flag}H',value))

    def write_Int32(self,value: int):
        self.file.write(struct.pack(f'{self.endian_flag}i',value))

    def write_UInt32(self,value: int):
        self.file.write(struct.pack(f'{self.endian_flag}I',value))

    def write_Int64(self,value: int):
        self.file.write(struct.pack(f'{self.endian_flag}q',value))

    def write_UInt64(self,value: int):
        self.file.write(struct.pack(f'{self.endian_flag}Q',value))

    def pad(self,alignment: int):
        mod = self.tell() % alignment
        if mod != 0:
            self.write(bytes(alignment - mod))