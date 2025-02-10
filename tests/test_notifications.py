import unittest
from unittest.mock import patch
import smtplib

class TestNotifications(unittest.TestCase):

    @patch("smtplib.SMTP")
    def test_email_notification(self, mock_smtp):
        """
        Tests if emails are sent from the CI server using mock unit tests in order to improve efficiency and safety.
        """
        mock_server = mock_smtp.return_value
        # change line below to incorporate file_name and function_name when those functions are implemented
        # file_name.function_name("Testing testing")

        mock_server.sendmail.assert_called()
        mock_server.quit.assert_called()

if __name__ == "__main__":
    unittest.main()