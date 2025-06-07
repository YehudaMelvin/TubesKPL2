import os
from flask import Flask, flash, redirect, render_template, request
from flasgger import Swagger
from repositories import BookRepository, MemberRepository, HistoryRepository


# Constants
BOOK_STATUS_TRANSITIONS = {
    "available": ["borrowed", "reserved"],
    "borrowed": ["returned"],
    "reserved": ["borrowed", "cancelled"],
    "returned": ["available"],
    "cancelled": ["available"]
}

HISTORY_FORMAT = {
    "template": "{book} dipinjam oleh {member} pada {borrowed} dan dikembalikan pada {returned}",
    "not_returned": "{book} dipinjam oleh {member} pada {borrowed} dan belum dikembalikan"
}

# Flask setup
app = Flask(__name__)
swagger = Swagger(app)
app.secret_key = 'supersecretkey'
# Utility

def format_history_entry(entry, books_dict, members_dict):
    book = books_dict.get(entry.get("book_id"), "Buku tidak ditemukan")
    member = members_dict.get(entry.get("member_id"), "Member tidak ditemukan")
    borrowed = entry.get("borrowed_at", entry.get("date", "-"))
    returned = entry.get("returned_at")

    if returned:
        return HISTORY_FORMAT["template"].format(book=book, member=member, borrowed=borrowed, returned=returned)
    else:
        return HISTORY_FORMAT["not_returned"].format(book=book, member=member, borrowed=borrowed)

def get_next_id(data_list):
    return max((item.get("id", 0) for item in data_list), default=0) + 1

# Routes

@app.route("/")
def show_home():
    return render_template("index.html")

@app.route("/books")
def list_books():
    books = BookRepository.get_all()
    return render_template("books.html", books=books)

@app.route("/add-book", methods=["GET", "POST"])
def add_new_book():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        if not title or not author:
            return "Judul dan penulis harus diisi.", 400

        books = BookRepository.get_all()
        new_book = {
            "id": get_next_id(books),
            "title": title,
            "author": author,
            "status": "available"
        }
        try:
            BookRepository.add(new_book)
        except Exception as e:
            app.logger.error(f"Gagal menambahkan buku: {e}")
            return "Gagal menyimpan data buku.", 500

        return redirect("/books")
    return render_template("add_book.html")

@app.route("/delete-book", methods=["GET", "POST"])
def remove_book():
    if request.method == "POST":
        try:
            book_id = int(request.form.get("book_id", "0"))
        except ValueError:
            return "ID buku tidak valid.", 400

        try:
            BookRepository.delete(book_id)
        except Exception as e:
            app.logger.error(f"Gagal menghapus buku: {e}")
            return "Gagal menghapus buku.", 500

        return redirect("/books")
    return render_template("delete_book.html")

@app.route("/search-books")
def search_books():
    query = request.args.get("q", "").strip().lower()
    books = BookRepository.get_all()
    if query:
        books = [b for b in books if query in b.get("title", "").lower() or query in b.get("author", "").lower()]
    return render_template("search_books.html", books=books, query=query)

@app.route("/update-status/<int:book_id>", methods=["GET", "POST"])
def update_book_status(book_id):
    books = BookRepository.get_all()
    book = next((b for b in books if b.get("id") == book_id), None)
    if not book:
        return "Buku tidak ditemukan", 404

    current_status = book.get("status")
    valid_transitions = BOOK_STATUS_TRANSITIONS.get(current_status, [])

    if request.method == "POST":
        new_status = request.form.get("status")
        try:
            member_id = int(request.form.get("member_id", "0"))
        except ValueError:
            return "ID anggota tidak valid.", 400

        if new_status not in valid_transitions:
            return f"Transisi tidak valid dari '{current_status}' ke '{new_status}'", 400

        # Special check for "returned"
        if new_status == "returned":
            borrowed_entry = None
            for entry in reversed(HistoryRepository.get_all()):
                if (entry["book_id"] == book_id
                    and entry["status"] == "borrowed"
                    and entry.get("returned_at") is None):
                    borrowed_entry = entry
                    break

            if borrowed_entry is None:
                return "Tidak ada peminjaman aktif untuk buku ini.", 400

            if borrowed_entry["member_id"] != member_id:
                return "Hanya member yang meminjam buku ini yang boleh mengembalikannya.", 403 

        # Update book status
        book["status"] = new_status
        try:
            BookRepository.update(book_id, book)

            # Only update history for "borrowed" or "returned"
            if new_status in ["borrowed", "returned"]:
                HistoryRepository.add(book_id, member_id, new_status)

        except Exception as e:
            app.logger.error(f"Gagal memperbarui status buku: {e}")
            return "Gagal memperbarui status.", 500

        return redirect("/books")

    members = MemberRepository.get_all()
    return render_template(
        "update_status.html",
        book=book,
        members=members,
        allowed_transitions=valid_transitions
    )

@app.route("/members")
def list_members():
    members = MemberRepository.get_all()
    return render_template("members.html", members=members)

@app.route("/add-member", methods=["GET", "POST"])
def add_new_member():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()

        if not name or not email:
            return "Nama dan email harus diisi.", 400

        members = MemberRepository.get_all()
        new_member = {
            "id": get_next_id(members),
            "name": name,
            "email": email
        }
        try:
            MemberRepository.add(new_member)
        except Exception as e:
            app.logger.error(f"Gagal menambahkan member: {e}")
            return "Gagal menyimpan data member.", 500

        return redirect("/members")
    return render_template("add_member.html")

@app.route("/update-member/<int:member_id>", methods=["GET", "POST"])
def update_member(member_id):
    members = MemberRepository.get_all()
    member = next((m for m in members if m.get("id") == member_id), None)
    if not member:
        return "Member tidak ditemukan", 404

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        if not name or not email:
            return "Nama dan email harus diisi.", 400
        member["name"] = name
        member["email"] = email
        try:
            MemberRepository.update(member_id, member)
        except Exception as e:
            app.logger.error(f"Gagal memperbarui member: {e}")
            return "Gagal memperbarui member.", 500
        return redirect("/members")

    return render_template("update_member.html", member=member)

@app.route("/delete-member", methods=["GET", "POST"])
def delete_member():
    if request.method == "POST":
        try:
            member_id = int(request.form.get("member_id", "0"))
        except ValueError:
            return "ID member tidak valid.", 400
        try:
            MemberRepository.delete(member_id)
        except Exception as e:
            app.logger.error(f"Gagal menghapus member: {e}")
            return "Gagal menghapus member.", 500
        return redirect("/members")
    return render_template("delete_member.html")

@app.route("/history")
def show_history():
    raw_history = HistoryRepository.get_all()
    books_dict = {b.get("id"): b.get("title") for b in BookRepository.get_all()}
    members_dict = {m.get("id"): m.get("name") for m in MemberRepository.get_all()}
    formatted_history = [format_history_entry(h, books_dict, members_dict) for h in raw_history]
    return render_template("history.html", history=formatted_history)

@app.route("/delete-history", methods=["GET", "POST"])
def delete_history():
    if request.method == "POST":
        try:
            index = int(request.form.get("index", "-1"))
        except ValueError:
            flash("Index tidak valid.")
            return redirect("/delete-history")

        history = HistoryRepository.get_all()
        history_length = len(history)

        if history_length == 0:
            flash("Tidak ada history yang dapat dihapus.")
            return redirect("/history")

        if index < 0 or index >= history_length:
            flash(f"Index {index} tidak tersedia. Index yang valid: 0 sampai {history_length - 1}.")
            return redirect("/delete-history")

        try:
            history.pop(index)
            HistoryRepository.save_all(history)
            flash(f"History pada index {index} berhasil dihapus.")
        except Exception as e:
            app.logger.error(f"Gagal menghapus history: {e}")
            flash("Terjadi kesalahan saat menghapus history.")

        return redirect("/history")

    # Untuk GET → tampilkan form hapus
    history = HistoryRepository.get_all()
    history_length = len(history)
    return render_template("delete_history.html", history_length=history_length)

if __name__ == "__main__":
    app.run(debug=False)


