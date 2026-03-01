# reset_db.py
from database import engine, Base
from sqlalchemy import inspect

print("Menghapus tabel lama...")
Base.metadata.drop_all(bind=engine)
print("Membuat ulang tabel dengan struktur baru...")
Base.metadata.create_all(bind=engine)
print("Selesai! Database sudah diperbarui.")
