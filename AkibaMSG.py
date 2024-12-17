from utils import EndianBinaryFileReader, EndianBinaryFileWriter
import os
from pathlib import Path
import sys
import pandas as pd

SKIPSCRIPT = ["mm_c2_0400_660.bin", "mm_c2_0400_670.bin", "mm_c2_0400_680.bin",  #some script files have a different format (16 less bytes per entry) and may fail the export -> we skip those
              "mm_c2_0400_690.bin", "mm_c2_0400_700.bin", "mm_c2_0400_710.bin",
              "script_talkevent_list.bin", "Template.bin", "test_010.bin",
              "test_020.bin", "test_030.bin", "test_040.bin",
              "test_saito_010.bin", "test_saito_020.bin", "mm_jb_1020_03.bin",
              "bt_0010.bin", "bt_0020.bin", "bt_0030.bin", "bt_0040.bin",
              ]

class AkibaGametext:
    def __init__(self, filepath : str):
        self.filename = os.path.basename(filepath)
        with EndianBinaryFileReader(filepath) as f:
            self.entry_count = f.read_Int32()
            self.start_offset = f.read_Int32()
            self.strings_offset = [f.read_Int32() for _ in range(self.entry_count)]
            self.strings : list[str] = []
            for offset in self.strings_offset:
                f.seek(offset + 8)
                string = (f.read_utf16_until_null())
                assert "{" not in string
                self.strings.append(string)
        
    def write_excel(self, out_dir):
        out_path = Path(out_dir) / "gametext" / (self.filename + '.xlsx')
        data = [[string, string] for string in self.strings]
        columns = ["Original","Translation"]
        df = pd.DataFrame(data=data, columns=columns)
        df.to_excel(out_path)

    def load_excel(self, excel_file : str):
        df = pd.read_excel(excel_file, index_col = 0, dtype = str, na_filter=False)
        self.strings = [str(data) for data in df["Translation"]]

    def save(self, out_dir):
        out_path = Path(out_dir) / "gametext" / self.filename
        with EndianBinaryFileWriter(out_path) as f:
            f.write_Int32(self.entry_count)
            f.write_Int32(self.start_offset)
            offset = 4 * self.entry_count
            out_strings = [(string + '\x00').encode('utf-16')[2:] for string in self.strings]
            for idx in range(self.entry_count):
                f.write_Int32(offset)
                offset += len(out_strings[idx])
            for string in out_strings:
                f.write(string)

class AkibaTaskChange:
    def __init__(self, filepath : str):
        self.filename = os.path.basename(filepath)
        with EndianBinaryFileReader(filepath) as f:
            self.entry_count = f.read_Int32()
            padding = f.read(12)
            self.entries = [TaskChangeEntry(f) for _ in range(self.entry_count)]

    def write_excel(self, out_dir):
        out_path = Path(out_dir) / "gametext" / (self.filename + '.xlsx')
        data = [[entry.string, entry.string] for entry in self.entries]
        columns = ["Original","Translation"]
        df = pd.DataFrame(data=data, columns=columns)
        df.to_excel(out_path)

    def load_excel(self, excel_file):
        df = pd.read_excel(excel_file, index_col = 0, dtype = str, na_filter=False)
        for idx, data in enumerate(df["Translation"]):
            self.entries[idx].string = str(data)

    def save(self, out_dir : str):
        out_path = Path(out_dir) / "gametext" / self.filename
        with EndianBinaryFileWriter(out_path) as f:
            f.write_Int32(self.entry_count)
            f.write(b"\x00" * 12)
            offset = self.entry_count * 12 + 0x10
            for entry in self.entries:
                string_offset = offset
                entry.string_bytes = (entry.string + '\x00\x00').encode('utf-16')[2:]
                string_size = len(entry.string_bytes)
                f.write_Int32(string_offset)
                f.write_Int32(string_size)
                f.write_Int32(0)
                offset += string_size
            for entry in self.entries:
                f.write(entry.string_bytes)


class TaskChangeEntry:
    def __init__(self, f : EndianBinaryFileReader):
        self.string_offset = f.read_Int32()
        self.string_size = f.read_Int32()
        padding = f.read_Int32()
        pos = f.tell()
        f.seek(self.string_offset)
        self.string = f.read(self.string_size).decode('utf-16')[:-2]
        f.seek(pos)

class AkibaScript:
    def __init__(self, filepath : str):
        self.filename = os.path.basename(filepath)
        with EndianBinaryFileReader(filepath) as f:
            padding = f.read(12)
            self.entry_count = f.read_Int32()
            self.string_start_offset = 0x10 + self.entry_count * 0x50
            self.entries = [ScriptEntry(f, self.string_start_offset) for _ in range(self.entry_count)]

    def write_excel(self, out_dir):
        out_path = Path(out_dir) / "script" / "talkevent" / (self.filename + '.xlsx')
        data = []
        for entry in self.entries:
            if entry.type == 1:
                data.append(["Dialogue", entry.string, entry.string])
            elif entry.type == 2:
                data.append(["Choice Caption", entry.caption_string, entry.caption_string])
                data.append(["Choice 1", entry.choice1_string, entry.choice1_string])
                data.append(["Choice 2", entry.choice2_string, entry.choice2_string])
                data.append(["Choice 3", entry.choice3_string, entry.choice3_string])

        columns = ["Type", "Original","Translation"]
        df = pd.DataFrame(data=data, columns=columns)
        df.to_excel(out_path)

    def load_excel(self, excel_file : str):
        df = pd.read_excel(excel_file, index_col = 0, dtype = str, na_filter=False)
        strings = iter([str(data) for data in df["Translation"]])
        for entry in self.entries:
            if entry.type == 1:
                entry.string = next(strings)
            if entry.type == 2:
                entry.caption_string = next(strings)
                entry.choice1_string = next(strings)
                entry.choice2_string = next(strings)
                entry.choice3_string = next(strings)

    def save(self, out_dir : str):
        out_path = Path(out_dir) / "script" / "talkevent" / self.filename
        with EndianBinaryFileWriter(out_path) as f:
            f.write(b"\x00" * 12)
            f.write_Int32(self.entry_count)
            f.write(b"\x00" * 0x50 * self.entry_count)
            for idx, entry in enumerate(self.entries):
                pos = 0x10 + 0x50 * idx
                f.seek(pos)
                f.write(entry.bytedata)
                if entry.type == 1:
                    f.seek(0, 2)
                    offset = f.tell() - self.string_start_offset
                    f.write((entry.string + '\x00').encode('utf-16')[2:])
                    f.seek(pos + 0x20)
                    f.write_UInt16(offset)
                elif entry.type == 2:
                    f.seek(0, 2)
                    caption_offset = f.tell() - self.string_start_offset
                    f.write((entry.caption_string + '\x00').encode('utf-16')[2:])
                    choice1_offset = f.tell() - self.string_start_offset
                    f.write((entry.choice1_string + '\x00').encode('utf-16')[2:])
                    choice2_offset = f.tell() - self.string_start_offset
                    f.write((entry.choice2_string + '\x00').encode('utf-16')[2:])
                    choice3_offset = f.tell() - self.string_start_offset
                    f.write((entry.choice3_string + '\x00').encode('utf-16')[2:])
                    f.seek(pos + 0x20)
                    f.write_UInt16(caption_offset)
                    f.seek(pos + 0x28)
                    f.write_UInt16(choice1_offset)
                    f.write_UInt16(choice2_offset)
                    f.write_UInt16(choice3_offset)

class ScriptEntry:
    def __init__(self, f : EndianBinaryFileReader, string_start_offset : int):
        pos = f.tell()
        self.bytedata = f.read(0x50)
        f.seek(pos)
        self.unk = f.read_Int16()
        self.type = f.read_Int16()
        self.param = f.read_Int16()

        if self.type == 1:
            f.seek(pos + 0x20)
            string_offset = f.read_UInt16()
            f.seek(string_offset + string_start_offset)
            self.string = f.read_utf16_until_null()

        elif self.type == 2:
            f.seek(pos + 0x20)
            caption_offset = f.read_UInt16()
            f.seek(pos + 0x28)
            choice1_string_offset = f.read_UInt16()
            choice2_string_offset = f.read_UInt16()
            choice3_string_offset = f.read_UInt16()
            f.seek(caption_offset + string_start_offset)
            self.caption_string = f.read_utf16_until_null()
            f.seek(choice1_string_offset + string_start_offset)
            self.choice1_string = f.read_utf16_until_null()
            f.seek(choice2_string_offset + string_start_offset)
            self.choice2_string = f.read_utf16_until_null()
            f.seek(choice3_string_offset + string_start_offset)
            self.choice3_string = f.read_utf16_until_null()

        f.seek(pos + 0x50)


def batch_export(in_dir, out_dir):
    if not (Path(out_dir) / "gametext").exists():
        os.makedirs(Path(out_dir) / "gametext")

    if not (Path(out_dir) / "script" / "talkevent").exists():
        os.makedirs(Path(out_dir) / "script" / "talkevent")

    gametext_path = Path(in_dir) / "gametext" / "gametext.bin"
    print("Exporting gametext.bin...")
    gametext = AkibaGametext(gametext_path)
    gametext.write_excel(out_dir)

    tasktext_path = Path(in_dir) / "gametext" / "TaskChangeText.bin"
    print("Exporting TaskChangeText.bin...")
    tasktext = AkibaTaskChange(tasktext_path)
    tasktext.write_excel(out_dir)

    for path in (Path(in_dir) / "script" / "talkevent").iterdir():
        if path.name in SKIPSCRIPT:
            continue
        print(f"Exporting {path}...")
        script = AkibaScript(path)
        script.write_excel(out_dir)

def batch_import(base_dir, modded_dir, new_dir):
    if not (Path(new_dir) / "gametext").exists():
        os.makedirs(Path(new_dir) / "gametext")

    if not (Path(new_dir) / "script" / "talkevent").exists():
        os.makedirs(Path(new_dir) / "script" / "talkevent")

    gametext_path = Path(base_dir) / "gametext" / "gametext.bin"
    print("Importing gametext.bin...")
    gametext = AkibaGametext(gametext_path)
    gametext.load_excel(Path(modded_dir) / "gametext" / "gametext.bin.xlsx")
    gametext.save(new_dir)

    tasktext_path = Path(base_dir) / "gametext" / "TaskChangeText.bin"
    print("Importing TaskChangeText.bin...")
    tasktext = AkibaTaskChange(tasktext_path)
    tasktext.load_excel(Path(modded_dir) / "gametext" / "TaskChangeText.bin.xlsx")
    tasktext.save(new_dir)

    for path in (Path(base_dir) / "script" / "talkevent").iterdir():
        if path.name in SKIPSCRIPT:
            continue
        excel_path = Path(modded_dir) / "script" / "talkevent" / f"{path.name}.xlsx"
        if excel_path.exists():
            print(f"Importing {path}...")
            script = AkibaScript(path)
            script.load_excel(Path(modded_dir) / "script" / "talkevent" / f"{path.name}.xlsx")
            script.save(new_dir)

def main():
    args = sys.argv
    if "-e" in args:
        batch_export(args[2], args[3])
    
    elif "-i" in args:
        batch_import(args[2], args[3], args[4])

if __name__ == '__main__':
    main()