import unittest
import sqlite3
import os
from app import app, DATABASE, initialize_database

class BankingAppV2TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        initialize_database()
        connection = sqlite3.connect(DATABASE)
        connection.execute("UPDATE account SET balance = 1000.0 WHERE id = 1")
        connection.commit()
        connection.close()

    def test_home_page_balance_display(self):
        """V2: Verify balance loading remains functional"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Current Balance", response.data)

    def test_successful_deposit(self):
        """V2: Verify deposit system logic works perfectly across versions"""
        response = self.app.post('/deposit', data={'amount': '250.50'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully deposited", response.data)
        self.assertIn(b"1250.50", response.data)

    def test_successful_withdrawal(self):
        """V2: Verify standard valid withdrawal requests correctly decrement the database record"""
        response = self.app.post('/withdraw', data={'w_amount': '400.00'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully withdrew", response.data)
        self.assertIn(b"600.00", response.data)

    def test_insufficient_funds_withdrawal(self):
        """V2: Verify overdraft attempt triggers balance rejection safety rule"""
        response = self.app.post('/withdraw', data={'w_amount': '1200.00'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Transaction failed: Insufficient balance", response.data)
        self.assertIn(b"1000.00", response.data)

    def test_invalid_negative_withdrawal(self):
        """V2: Verify negative format values trigger bad validation errors"""
        response = self.app.post('/withdraw', data={'w_amount': '-50.00'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid withdrawal amount", response.data)

if __name__ == '__main__':
    unittest.main()