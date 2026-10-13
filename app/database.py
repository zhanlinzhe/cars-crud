"""SQLite CRUD using only the Python standard library. No ORM."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from app.schemas import Car, CarInput


@contextmanager
def connect(database_path: Path) -> Iterator[sqlite3.Connection]:
    # A fresh connection per operation keeps connections on their owning thread.
    connection = sqlite3.connect(database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        # Commit on success, roll back on failure.
        with connection:
            yield connection
    finally:
        # sqlite3's connection context manager does NOT close the connection.
        connection.close()


def initialize(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS cars (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                make TEXT NOT NULL CHECK(length(trim(make)) BETWEEN 1 AND 60),
                model TEXT NOT NULL CHECK(length(trim(model)) BETWEEN 1 AND 60),
                year INTEGER NOT NULL CHECK(year BETWEEN 1886 AND 2100),
                color TEXT NOT NULL DEFAULT '' CHECK(length(color) <= 40)
            )
            """
        )


def list_cars(database_path: Path) -> list[Car]:
    with connect(database_path) as connection:
        rows = connection.execute("SELECT * FROM cars ORDER BY id DESC").fetchall()
        return [Car(**dict(row)) for row in rows]


def get_car(database_path: Path, car_id: int) -> Car | None:
    with connect(database_path) as connection:
        row = connection.execute("SELECT * FROM cars WHERE id = ?", (car_id,)).fetchone()
        print("===== get_car =====", flush=True)
        print("database_path =", database_path, flush=True)
        print("car_id =", car_id, flush=True)
        print("数据库里的行 =", dict(row) if row else None, flush=True)
        return Car(**dict(row)) if row is not None else None


def create_car(database_path: Path, car: CarInput) -> Car:
    with connect(database_path) as connection:
        cursor = connection.execute(
            "INSERT INTO cars (make, model, year, color) VALUES (?, ?, ?, ?)",
            (car.make, car.model, car.year, car.color),
        )
        return Car(id=cursor.lastrowid, **car.model_dump())


def update_car(database_path: Path, car_id: int, car: CarInput) -> Car | None:
    print("===== database.update_car 开始 =====", flush=True)
    print("database_path =", database_path, flush=True)
    print("car_id =", car_id, flush=True)
    print("car =", car.model_dump(), flush=True)
    with connect(database_path) as connection:
        cursor = connection.execute(
            "UPDATE cars SET make = ?, model = ?, year = ?, color = ? WHERE id = ?",
            (car.make, car.model, car.year, car.color, car_id),
        )
        print("cursor.rowcount =", cursor.rowcount, flush=True)
        if cursor.rowcount == 0:
            print("rowcount 是 0，返回 None", flush=True)
            return None
        # 验证写入是否生效
        row = connection.execute("SELECT * FROM cars WHERE id = ?", (car_id,)).fetchone()
        print("写完后数据库里的行 =", dict(row) if row else None, flush=True)
        return Car(id=car_id, **car.model_dump())


def delete_car(database_path: Path, car_id: int) -> bool:
    with connect(database_path) as connection:
        cursor = connection.execute("DELETE FROM cars WHERE id = ?", (car_id,))
        return cursor.rowcount == 1
