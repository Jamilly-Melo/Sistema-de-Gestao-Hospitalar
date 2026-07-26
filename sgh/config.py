"""Configuração de conexão, lida do ambiente.

Os defaults são os do docker-compose, onde o frontend fala com o Postgres pelo
hostname `database` na porta interna 5432. Para rodar fora do container, exporte
DB_HOST=localhost e DB_PORT=5435 (a porta publicada no host).
"""

import os

DB_HOST = os.getenv("DB_HOST", "database")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "sgh_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
