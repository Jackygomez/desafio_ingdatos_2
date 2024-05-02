import unittest
from unittest.mock import patch, MagicMock
from data_access import connect_to_sql_server, fetch_coordinates

class TestDataAccess(unittest.TestCase):

    @patch('data_access.pyodbc.connect')
    def test_connect_to_sql_server(self, mock_connect):
        connect_to_sql_server()
        mock_connect.assert_called_once()

    @patch('data_access.connect_to_sql_server')
    def test_fetch_coordinates(self, mock_connect):
        # Simular la conexión y el cursor
        mock_conn = mock_connect.return_value.__enter__.return_value
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchall.return_value = [(1, '52.629729', '-1.131592')]

        result = fetch_coordinates()
        self.assertEqual(result, [(1, '52.629729', '-1.131592')])
        mock_cursor.execute.assert_called_once_with("SELECT id, latitude, longitude FROM coordinates")

if __name__ == '__main__':
    unittest.main()
