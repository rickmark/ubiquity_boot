import struct
import io

HEADER_MAGIC = b'UBNT'
FILE_MAGIC = b'FILE'
SIGNATURE_MAGIC = b'ENDS'
MAGIC_LENGTH = 4

HEADER_FORMAT = '4s256sII'
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

FILE_ENTRY_HEADER_FORMAT = '>44sII'
FILE_ENTRY_HEADER_SIZE = struct.calcsize(FILE_ENTRY_HEADER_FORMAT)

FILE_ENTRY_FOOTER_FORMAT = 'II'
FILE_ENTRY_FOOTER_SIZE = struct.calcsize(FILE_ENTRY_FOOTER_FORMAT)

SIGNATURE_FORMAT = '256sI'
SIGNATURE_SIZE = struct.calcsize(SIGNATURE_FORMAT)


class InvalidDataError(RuntimeError):
    pass


class FirmwareFileEntry(object):
    def __init__(self, stream):
        self.stream = stream
        self.pos = stream.seek(0, io.SEEK_CUR) - MAGIC_LENGTH
        entry_name, self.length, self.flags = struct.unpack(FILE_ENTRY_HEADER_FORMAT, stream.read(FILE_ENTRY_HEADER_SIZE))
        self.name = entry_name.rstrip(b'\0')
        self.start = stream.seek(0, io.SEEK_CUR)
        stream.seek(self.length, io.SEEK_CUR)
        self.checksum, skip = struct.unpack(FILE_ENTRY_FOOTER_FORMAT, stream.read(FILE_ENTRY_FOOTER_SIZE))
        stream.seek(skip, io.SEEK_CUR)

    def extract(self, output):
        if isinstance(output, str):
            output = io.FileIO(output, 'wb')

        self.stream.seek(self.pos, io.SEEK_SET)

        while True:
            buffer = self.stream.read(1024 * 64)

            if buffer == b'':
                break

            output.write(buffer)


class FirmwareSignature(object):
    def __init__(self, stream):
        self.pos = stream.seek(0, io.SEEK_CUR) - MAGIC_LENGTH
        self.signature, self.key = struct.unpack(SIGNATURE_FORMAT, stream.read(SIGNATURE_SIZE))


class FirmwareParser(object):
    def __init__(self, source):
        if isinstance(source, str):
            self.stream = io.FileIO(source, mode='rb')
            self.filename = source
        else:
            self.stream = source
            self.filename = None

        magic, name, checksum, skip = struct.unpack(HEADER_FORMAT, self.stream.read(HEADER_SIZE))
        if magic != HEADER_MAGIC:
            raise InvalidDataError(f'invalid header magic {magic}')

        self._name = name.rstrip(b'\0').decode('utf-8')
        self.files = {}
        self.signature = None
        self.stream.seek(skip, io.SEEK_CUR)

    @property
    def name(self):
        return self._name


    def extract_all(self):
        for name in self.files:
            entry = self.files[name]
            entry.extract(name)


    def parse(self):
        while True:
            chunk = self.stream.read(4)

            if chunk == b'':
                break

            if chunk is None:
                break

            if chunk == FILE_MAGIC:
                file_entry = FirmwareFileEntry(self.stream)
                self.files[file_entry.name] = file_entry

            if chunk == SIGNATURE_MAGIC:
                self.signature = FirmwareSignature(self.stream)
