import json
import os
from datetime import datetime

DATA_DIR = "data"

def _read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def _write_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        json.dump(data, f, indent=4)

class BookRepository:
    FILENAME = "books.json"

    @staticmethod
    def get_all():
        return _read_json(BookRepository.FILENAME)

    @staticmethod
    def get_by_id(book_id):
        return next((b for b in BookRepository.get_all() if b["id"] == book_id), None)

    @staticmethod
    def save_all(data):
        _write_json(BookRepository.FILENAME, data)

    @staticmethod
    def add(book):
        books = BookRepository.get_all()
        books.append(book)
        BookRepository.save_all(books)

    @staticmethod
    def delete(book_id):
        books = BookRepository.get_all()
        books = [b for b in books if b["id"] != book_id]
        BookRepository.save_all(books)

    @staticmethod
    def update(book_id, updated_book):
        books = BookRepository.get_all()
        for i, book in enumerate(books):
            if book["id"] == book_id:
                books[i] = updated_book
                break
        BookRepository.save_all(books)

class MemberRepository:
    FILENAME = "members.json"

    @staticmethod
    def get_all():
        return _read_json(MemberRepository.FILENAME)

    @staticmethod
    def add(member):
        members = MemberRepository.get_all()
        members.append(member)
        _write_json(MemberRepository.FILENAME, members)

    @staticmethod
    def update(member_id, updated_member):
        members = MemberRepository.get_all()
        for i, m in enumerate(members):
            if m["id"] == member_id:
                members[i] = updated_member
                break
        _write_json(MemberRepository.FILENAME, members)

    @staticmethod
    def delete(member_id):
        members = MemberRepository.get_all()
        members = [m for m in members if m["id"] != member_id]
        _write_json(MemberRepository.FILENAME, members)


class HistoryRepository:
    FILENAME = "history.json"

    @staticmethod
    def get_all():
        return _read_json(HistoryRepository.FILENAME)

    @staticmethod
    def add(book_id, member_id, status):
        history = HistoryRepository.get_all()
        history.append({
            "book_id": book_id,
            "member_id": member_id,
            "status": status,
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        _write_json(HistoryRepository.FILENAME, history)

    @staticmethod
    def save_all(history_data):
        _write_json(HistoryRepository.FILENAME, history_data)
