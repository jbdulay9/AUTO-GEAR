import mysql.connector
from mysql.connector import Error, pooling
from backend.config import Config


class DatabaseManager:
    """
    OOP Manager for MySQL database operations.
    Encapsulates connection pooling, parameterized execution, and transaction safety.
    """

    def __init__(
        self,
        host=None,
        port=None,
        user=None,
        password=None,
        database=None,
        pool_name="autogear_pool",
        pool_size=5,
    ):
        self.host = host or Config.DB_HOST
        self.port = port or Config.DB_PORT
        self.user = user or Config.DB_USER
        self.password = password or Config.DB_PASSWORD
        self.database = database or Config.DB_NAME
        self.pool_name = pool_name
        self.pool_size = pool_size
        self._pool = None

    def init_pool(self):
        """Initializes a thread-safe connection pool for MySQL."""
        if self._pool is None:
            try:
                self._pool = pooling.MySQLConnectionPool(
                    pool_name=self.pool_name,
                    pool_size=self.pool_size,
                    pool_reset_session=True,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )
            except Error as e:
                print(f"[DatabaseManager Error] Failed to initialize connection pool: {e}")
                raise e

    def get_connection(self):
        """Retrieves an active connection from the pool."""
        if self._pool is None:
            self.init_pool()
        return self._pool.get_connection()

    def test_connection(self):
        """Verifies database connectivity and returns a status dictionary."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT 1 AS connected, DATABASE() AS db_name;")
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            return {"success": True, "data": result}
        except Error as e:
            return {"success": False, "error": str(e)}

    def execute_query(self, query, params=None, commit=False):
        """
        Executes an INSERT, UPDATE, or DELETE parameterized query.
        If commit=True, commits the transaction. Automatically rolls back on failure.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params or ())
            if commit:
                conn.commit()
            last_id = cursor.lastrowid
            row_count = cursor.rowcount
            return {"lastrowid": last_id, "rowcount": row_count}
        except Error as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()

    def fetch_one(self, query, params=None):
        """Executes a parameterized SELECT query and returns a single row as a dictionary."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    def fetch_all(self, query, params=None):
        """Executes a parameterized SELECT query and returns all matching rows as dictionaries."""
        conn = self.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, params or ())
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()


# Singleton default manager instance
_default_db_manager = DatabaseManager()


def get_db_manager():
    """Returns the default DatabaseManager instance."""
    return _default_db_manager


# Backward-compatible module functions for Phase 1 code
def init_pool():
    _default_db_manager.init_pool()


def get_connection():
    return _default_db_manager.get_connection()


def test_connection():
    return _default_db_manager.test_connection()


def execute_query(query, params=None, commit=False):
    return _default_db_manager.execute_query(query, params, commit)


def fetch_one(query, params=None):
    return _default_db_manager.fetch_one(query, params)


def fetch_all(query, params=None):
    return _default_db_manager.fetch_all(query, params)
