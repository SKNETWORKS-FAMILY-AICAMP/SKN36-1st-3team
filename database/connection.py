import os
import ssl

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_engine():
    url = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        f"?charset=utf8mb4"
    )

    return create_engine(
        url,
        connect_args={
            "ssl": {
                "check_hostname": False
            }
        },
        pool_pre_ping=True,
        pool_recycle=300,
    )


def test_connection():
    engine = get_engine()

    with engine.connect() as conn:
        result = conn.execute(text("SELECT DATABASE(), VERSION();"))
        row = result.fetchone()

        print("✅ MySQL 연결 성공")
        print(f"Database : {row[0]}")
        print(f"MySQL    : {row[1]}")


if __name__ == "__main__":
    test_connection()