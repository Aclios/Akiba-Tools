from utils import EndianBinaryFileReader, EndianBinaryFileWriter, try_create_dir_from_filepath
import zlib
from pathlib import Path
import sys

class Volume:
    def __init__(self, filepath : str):
        self.filepath = filepath
        with EndianBinaryFileReader(filepath, endianness = 'big') as f:
            self.magic = f.read(4)
            assert self.magic == b"\xFA\xDE\xBA\xBE", "Invalid magic"
            self.entry_count1 = f.read_UInt32()
            self.entry_count2 = f.read_UInt32()
            self.data_start_offset = f.read_UInt32()
            self.datasize = f.read_UInt32() # it takes into account an hypothetical padding of the last file which doesn't exist in reality
            assert self.entry_count1 == self.entry_count2
            self.entries = [VolumeEntry(f, self.data_start_offset) for _ in range(self.entry_count1)]

    def unpack(self, root_dir : str):
        with EndianBinaryFileReader(self.filepath, endianness = 'big') as f:
            for entry in self.entries:
                print(f"Extracting {entry.path}...")
                f.seek(entry.data_offset)
                data = f.read(entry.path_offset - entry.data_offset)
                if entry.compression_flag == 0:
                    pass
                elif entry.compression_flag == 8:
                    data = zlib.decompress(data)
                else:
                    raise Exception(f"Unsupported compression flag: {entry.compression_flag}")
                try_create_dir_from_filepath(Path(root_dir) / entry.path)
                open(Path(root_dir) / entry.path, 'wb').write(data)

    def import_files(self, root_dir : str, volume_path : str):
        with EndianBinaryFileWriter(volume_path, endianness = 'big') as fw:
            fw.write(self.magic)
            fw.write_UInt32(self.entry_count1)
            fw.write_UInt32(self.entry_count2)
            fw.write_UInt32(self.data_start_offset)
            fw.write_UInt32(0)
            fw.pad(self.data_start_offset)
            with EndianBinaryFileReader(self.filepath, endianness = 'big') as fr:
                for idx, entry in enumerate(self.entries):
                    print(f'Importing {entry.path}')
                    fpath = Path(root_dir) / entry.path

                    if fpath.is_file():
                        data = open(fpath, 'rb').read()
                        decompressed_size = len(data)
                        if entry.compression_flag == 0:
                            pass
                        elif entry.compression_flag == 8:
                            data = zlib.compress(data)
                        else:
                            raise Exception(f"Unsupported compression flag: {entry.compression_flag}")

                    else:
                        fr.seek(entry.data_offset)
                        data = fr.read(entry.path_offset - entry.data_offset)
                        decompressed_size = entry.decompressed_data_size

                    data_offset = fw.tell() - self.data_start_offset
                    fw.write(data)
                    path_offset = fw.tell() - self.data_start_offset
                    fw.write(entry.path.encode('utf-8'))
                    if fw.tell() % 0x800 == 0:
                        fw.write(b'\x00' * 800)
                    else:
                        fw.pad(0x800)
                    pos = fw.tell()
                    fw.seek((0x18 * idx) + 0x14)
                    fw.write_UInt32(entry.unk_offset)
                    fw.write_UInt32(data_offset)
                    fw.write_UInt32(decompressed_size)
                    fw.write_UInt32(entry.compression_flag)
                    fw.write_UInt32(path_offset)
                    fw.write_UInt32(entry.unk)
                    fw.seek(pos)
                fw.seek(0x10)
                fw.write_UInt32(pos - self.data_start_offset) # datasize

class VolumeEntry:
    def __init__(self, f : EndianBinaryFileReader, data_start_offset : int):
        self.unk_offset = f.read_UInt32()
        self.data_offset = f.read_UInt32() + data_start_offset
        self.decompressed_data_size = f.read_UInt32()
        self.compression_flag = f.read_UInt32()
        self.path_offset = f.read_UInt32() + data_start_offset
        self.unk = f.read_UInt32()
        pos = f.tell()
        f.seek(self.path_offset)
        self.path = f.read_string_until_null('utf-8')
        f.seek(pos)

def main():
    args = sys.argv
    if "-e" in args:
        vol = Volume(args[2])
        vol.unpack(args[3])

    if "-i" in args:
        vol = Volume(args[2])
        vol.import_files(args[3], args[4])

if __name__ == '__main__':
    main()