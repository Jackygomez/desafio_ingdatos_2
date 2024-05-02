import unittest
from unittest.mock import patch
from business_logic import process_csv_file

class TestBusinessLogic(unittest.TestCase):

    @patch('business_logic.store_csv_async')
    def test_process_csv_file(self, mock_store_csv_async):
        file = MagicMock()
        file.stream.read().decode.return_value = 'lat|lon\n52.629729|-1.131592'
        message, status = process_csv_file(file)
        self.assertEqual(status, 202)
        self.assertEqual(message, "File is being processed")
        mock_store_csv_async.assert_called_once()

if __name__ == '__main__':
    unittest.main()
