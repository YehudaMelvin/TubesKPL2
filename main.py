import json
import os
from flask import Flask, redirect, render_template, request
from flasgger import Swagger
from datetime import datetime

DATA_DIR = "data"

def get_item_by_id(data, item_id):
    """Cari satu item dari list berdasarkan ID."""
    return next((item for item in data if item["id"] == item_id), None)

def get_new_id(data):
    """Menghasilkan ID baru berdasarkan data yang sudah ada."""
    return max((item["id"] for item in data), default=0) + 1

def delete_item_by_id(data, item_id):
    """Menghapus item berdasarkan ID."""
    return [item for item in data if item["id"] != item_id]

def append_history_entry(book_id, member_id, status):
    history = read_json("history.json")
    new_entry = {
        "book_id": book_id,
        "member_id": member_id,
        "status": status,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    history.append(new_entry)
    write_json("history.json", history)

def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def write_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        json.dump(data, f, indent=4)

app = Flask(__name__)
swagger = Swagger(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/books")
def books_list():
    books = read_json("books.json")
    return render_template("books.html", books=books)

@app.route("/add-book", methods=["GET", "POST"])
def add_book():
    books = read_json("books.json")
    if request.method == "POST":
        new_id = get_new_id(books)
        books.append({
            "id": new_id,
            "title": request.form["title"],
            "author": request.form["author"],
            "status": "available"
        })
        write_json("books.json", books)
        return redirect("/books")
    return render_template("add_book.html")

@app.route("/delete-book", methods=["GET", "POST"])
def delete_book():
    books = read_json("books.json")
    if request.method == "POST":
        book_id = int(request.form["book_id"])
        books = delete_item_by_id(books, book_id)
        write_json("books.json", books)
        return redirect("/books")
    return render_template("delete_book.html")

@app.route("/search-books", methods=["GET"])
def search_books():
    query = request.args.get("q", "").lower()
    books = read_json("books.json")
    if query:
        books = [book for book in books if query in book["title"].lower() or query in book["author"].lower()]
    return render_template("search_books.html", books=books, query=query)


@app.route("/update-status/<int:book_id>", methods=["GET", "POST"])
def update_status(book_id):
    books = read_json("books.json")
    book = get_item_by_id(books, book_id)
    if not book:
        return "Book not found", 404

    if request.method == "POST":
        new_status = request.form["status"]
        member_id = int(request.form["member_id"])

        book["status"] = new_status
        write_json("books.json", books)

        append_history_entry(book_id, member_id, new_status)
        return redirect("/books")

    members = read_json("members.json")
    return render_template("update_status.html", book=book, members=members)


# Table for valid status transitions
BOOK_STATUS_TABLE = {
    "available": ["borrowed", "reserved"],
    "borrowed": ["returned"],
    "reserved": ["borrowed", "cancelled"],
    "returned": ["available"],
    "cancelled": ["available"]
}


@app.route("/members")
def members_list():
    members = read_json("members.json")
    return render_template("members.html", members=members)

@app.route("/add-member", methods=["GET", "POST"])
def add_member():
    members = read_json("members.json")
    if request.method == "POST":
        new_id = max((m["id"] for m in members), default=0) + 1
        name = request.form["name"]
        email = request.form["email"]

        members.append({
            "id": new_id,
            "name": name,
            "email": email
        })

        write_json("members.json", members)
        return redirect("/members")
    return render_template("add_member.html")

HISTORY_FORMAT_TABLE = {
    "template": "{book} dipinjam oleh {member} pada {borrowed} dan dikembalikan pada {returned}",
    "not_returned": "{book} dipinjam oleh {member} pada {borrowed} dan belum dikembalikan"
}

def format_history_entry(entry, books, members):
    book = books.get(entry["book_id"], "Buku tidak ditemukan")
    member = members.get(entry["member_id"], "Member tidak ditemukan")
    borrowed = entry.get("borrowed_at", "-")
    returned = entry.get("returned_at")
    if returned:
        return HISTORY_FORMAT_TABLE["template"].format(book=book, member=member, borrowed=borrowed, returned=returned)
    else:
        return HISTORY_FORMAT_TABLE["not_returned"].format(book=book, member=member, borrowed=borrowed)

@app.route("/history")
def history_list():
    raw_history = read_json("history.json")
    books = {b["id"]: b["title"] for b in read_json("books.json")}
    members = {m["id"]: m["name"] for m in read_json("members.json")}
    history = [format_history_entry(h, books, members) for h in raw_history]
    return render_template("history.html", history=history)


if __name__ == "__main__":
    app.run(debug=True)
