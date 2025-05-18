import json
import os
from flask import Flask, redirect, render_template, request

# Lokasi folder data
DATA_DIR = "data"

# Fungsi bantu baca JSON
def read_json(filename):
    path = os.path.join(DATA_DIR, filename)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

# Fungsi bantu tulis JSON
def write_json(filename, data):
    with open(os.path.join(DATA_DIR, filename), "w") as f:
        json.dump(data, f, indent=4)

app = Flask(__name__)

# ------------------- HOME -----------------------
@app.route("/")
def home():
    return render_template("index.html")

# ------------------- BOOKS -----------------------
@app.route("/books")
def books_list():
    data = read_json("books.json")
    columns = [
        {"header": "ID", "key": "id"},
        {"header": "Judul", "key": "title"},
        {"header": "Penulis", "key": "author"},
        {"header": "Status", "key": "status"},
    ]
    return render_template("books.html", data=data, columns=columns)

@app.route("/add-book", methods=["GET", "POST"])
def add_book():
    books = read_json("books.json")
    if request.method == "POST":
        new_id = max((book["id"] for book in books), default=0) + 1
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
        books = [b for b in books if b["id"] != book_id]
        write_json("books.json", books)
        return redirect("/books")
    return render_template("delete_book.html")

@app.route("/update-status/<int:book_id>", methods=["GET", "POST"])
def update_status(book_id):
    books = read_json("books.json")
    book = next((b for b in books if b["id"] == book_id), None)
    if not book:
        return "Book not found", 404
    if request.method == "POST":
        book["status"] = request.form["status"]
        write_json("books.json", books)
        return redirect("/books")
    return render_template("update_status.html", book=book)

# ------------------- MEMBERS -----------------------
@app.route("/members")
def members_list():
    data = read_json("members.json")
    columns = [
        {"header": "ID", "key": "id"},
        {"header": "Nama", "key": "name"},
        {"header": "Email", "key": "email"},
    ]
    return render_template("members.html", data=data, columns=columns)

# ------------------- HISTORY -----------------------
@app.route("/history")
def history_list():
    history = read_json("history.json")
    books = {b["id"]: b["title"] for b in read_json("books.json")}
    members = {m["id"]: m["name"] for m in read_json("members.json")}

    data = []
    for h in history:
        data.append({
            "Buku": books.get(h["book_id"], "Tidak ditemukan"),
            "Anggota": members.get(h["member_id"], "Tidak ditemukan"),
            "Tanggal Pinjam": h["borrowed_at"],
            "Tanggal Kembali": h["returned_at"] or "Belum dikembalikan"
        })

    columns = [
        {"header": "Buku", "key": "Buku"},
        {"header": "Anggota", "key": "Anggota"},
        {"header": "Tanggal Pinjam", "key": "Tanggal Pinjam"},
        {"header": "Tanggal Kembali", "key": "Tanggal Kembali"},
    ]
    return render_template("history.html", data=data, columns=columns)

# ------------------- RUN -----------------------
if __name__ == "__main__":
    app.run(debug=True)
