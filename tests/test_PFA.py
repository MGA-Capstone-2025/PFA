import pytest
import sqlite3
import os
from src.PersonalFinanceApp import (
    initialize_db, create_user, verify_user, add_transaction,
    load_transactions, calculate_total_balance, hash_password
)
DB_NAME = "finance_manager.db"


@pytest.fixture(scope="module")
def setup_db():
    # Setup: Initialize the test database
    initialize_db()
    yield
    # Teardown: Remove the test database
    os.remove(DB_NAME)


def test_initialize_db(setup_db):
    # Check if the database file is created
    assert os.path.exists(DB_NAME)

    # Check if the tables are created
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        assert cursor.fetchone() is not None
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='transactions'")
        assert cursor.fetchone() is not None


def test_create_user(setup_db):
    # Test creating a new user
    assert create_user("testuser", "testpassword") is True

    # Test creating a user with an existing username
    assert create_user("testuser", "testpassword") is False


def test_verify_user(setup_db):
    # Test verifying a user with correct credentials
    user_id = verify_user("testuser", "testpassword")
    assert user_id is not None

    # Test verifying a user with incorrect credentials
    assert verify_user("testuser", "wrongpassword") is None


def test_add_transaction(setup_db):
    user_id = verify_user("testuser", "testpassword")
    assert user_id is not None

    # Test adding a transaction
    add_transaction(user_id, 100.0, "Test Income", "Income")
    transactions = load_transactions(user_id)
    assert len(transactions) == 1
    assert transactions[0][0] == 100.0
    assert transactions[0][1] == "Test Income"
    assert transactions[0][2] == "Income"


def test_calculate_total_balance(setup_db):
    user_id = verify_user("testuser", "testpassword")
    assert user_id is not None

    # Test calculating total balance
    balance = calculate_total_balance(user_id)
    assert balance == 100.0

    # Add another transaction and test the balance again
    add_transaction(user_id, -50.0, "Test Expense", "Expense")
    balance = calculate_total_balance(user_id)
    assert balance == 50.0
