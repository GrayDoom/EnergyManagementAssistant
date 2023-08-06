import os
import xml.etree.ElementTree as ET

CONFIG_FILE = 'config.xml'

def load_config():
    return ET.parse(CONFIG_FILE).getroot()

def get_header():
    config = load_config()
    return config.find('.//Log/header').text.split(',')

def set_header(header):
    config = load_config()
    config.find('.//Log/header').text = ','.join(header)
    config.write(CONFIG_FILE)

def get_file_path():
    # file path of main.py. Work with Windows only
    return "python " + os.path.dirname(os.path.abspath(__file__)) + "\main.py"

def get_part(part_name):
    config = load_config()
    return config.find(f'.//Task/{part_name}').text.strip()

def get_prompt():
    intro = get_part('intro')
    rest = get_part('rest')
    end = get_part('end')
    header = ','.join(get_header())
    return intro + get_file_path() + rest + header + end

