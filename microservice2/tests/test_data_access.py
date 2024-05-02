import unittest
from unittest.mock import patch, MagicMock
from data_access import fetch_coordinates, update_postcode, connect_to_sql_server

class TestDataAccess(unittest.TestCase):

    @patch('data_access.pyodbc.connect')
    def test_connect_to_sql_server(self, mock_connect):
        connect_to_sql_server()
        mock_connect.assert_called_once_with("Driver={ODBC Driver 18 for SQL Server};Server=test_server,1433;Database=employeedirectorydb;UID=test_user;Pwd=test_pass;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=220;")

    @patch('data_access.connect_to_sql_server')
    def test_fetch_coordinates(self, mock_connect):
        mock_conn = mock_connect.return_value.__enter__.return_value
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, '52.629729', '-1.131592')]

        result = fetch_coordinates()
        self.assertEqual(result, [(1, '52.629729', '-1.131592')])
        mock_cursor.execute.assert_called_once_with("SELECT id, latitude, longitude FROM coordinates")

    @patch('data_access.connect_to_sql_server')
    def test_update_postcode(self, mock_connect):
        mock_conn = mock_connect.return_value.__enter__.return_value
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor

        update_postcode(1, 'LE1 1FA')
        mock_cursor.execute.assert_called_once_with("UPDATE coordinates SET postcode = ? WHERE id = ?", ('LE1 1FA', 1))
        mock_conn.commit.assert_called_once()

if __name__ == '__main__':
    unittest.main()
