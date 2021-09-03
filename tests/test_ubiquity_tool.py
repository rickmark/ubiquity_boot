from ubiquity_tool import __version__
from ubiquity_tool.firmware_parser import FirmwareParser

import os
import pytest


def test_version():
    assert __version__ == '0.1.0'


dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, 'test_data/210e-udmpro-1.10.0-6cc49445340f4896959ab66f6f1b8da3.bin')


@pytest.fixture(scope='module', autouse=True)
def parsed_firmware():
    parser = FirmwareParser(filename)
    parser.parse()
    return parser


def test_parse_file(parsed_firmware):
    assert parsed_firmware is not None


def test_firmware_name(parsed_firmware):
    assert parsed_firmware.name == 'UDM.alpinev2.v1.10.0.a2edd0c.210709.0332'


def test_firmware_file_count(parsed_firmware):
    assert len(parsed_firmware.files) == 6
    for file in parsed_firmware.files:
        print(f"File: {file}")


def test_firmware_extract_all(parsed_firmware):
    parsed_firmware.extract_all()