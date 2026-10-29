import unittest
import sqlite3
import os
from app import app, DATABASE, initialize_database

class BankingAppV1TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        initialize_database()
        connection = sqlite3.connect(DATABASE)
        connection.execute("UPDATE account SET balance = 1000.0 WHERE id = 1")
        connection.commit()
        connection.close()

    def test_home_page_balance_display(self):
        """V1: Verify home page loads status 200 and renders balance information"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Current Balance", response.data)
        self.assertIn(b"1000.00", response.data)

    def test_successful_deposit(self):
        """V1: Verify depositing a positive numerical amount increments the balance record"""
        response = self.app.post('/deposit', data={'amount': '500.00'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Successfully deposited", response.data)
        self.assertIn(b"1500.00", response.data)

    def test_invalid_negative_deposit(self):
        """V1: Verify negative currency deposits fail input filter validation rules"""
        response = self.app.post('/deposit', data={'amount': '-100.00'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Invalid deposit amount", response.data)

if __name__ == '__main__':
    unittest.main()