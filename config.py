import os
from .config import *

# Konfigurasi umum
THRESHOLD = 0.8
MAX_BOOKS_PER_MEMBER = 5
DATA_DIR = "data"

# Mode aplikasi
DEBUG = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

BOOKS_FILE = os.path.join(DATA_DIR, 'books.json')
MEMBERS_FILE = os.path.join(DATA_DIR, 'members.json')
HISTORY_FILE = os.path.join(DATA_DIR, 'history.json')