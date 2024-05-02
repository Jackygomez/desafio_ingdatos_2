import unittest
from unittest.mock import patch, MagicMock
from postcode_logic import get_and_update_postcodes

class TestPostcodeLogic(unittest.TestCase):

    @patch('postcode_logic.fetch_coordinates')
    @patch('postcode_logic.update_postcode')
    @patch('postcode_logic.requests.get')
    def test_get_and_update_postcodes(self, mock_get, mock_update, mock_fetch):
        mock_fetch.return_value = [(1, '52.629729', '-1.131592')]
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'status': 200,
            'result': [{'postcode': 'LE1 1FA'}]
        }
        mock_get.return_value = mock_response

        postcodes, errors = get_and_update_postcodes()

        self.assertEqual(postcodes, ['LE1 1FA'])
        self.assertEqual(errors, [])
        mock_update.assert_called_once_with(1, 'LE1 1FA')

if __name__ == '__main__':
    unittest.main()
