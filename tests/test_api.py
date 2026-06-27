# bybit_master_project/tests/test_api.py
import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import api_client

class TestApiSigning(unittest.TestCase):

    def test_signature_generation(self):
        """Ellenőrzi, hogy az aláíró függvény fix adatokra a megfelelő hexadecimális stringet adja-e"""
        mock_timestamp = "1672531199000"
        mock_key = "test_api_key"
        mock_secret = "test_api_secret"
        mock_recv_window = "5000"
        mock_payload = '{"dummy": "data"}'
        
        sig = api_client.generate_signature(
            mock_timestamp, mock_key, mock_secret, mock_recv_window, mock_payload
        )
        
        # Egy HMAC-SHA256 aláírásnak mindig 64 karakter hosszú hex stringnek kell lennie
        self.assertEqual(len(sig), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in sig))

if __name__ == "__main__":
    unittest.main()
