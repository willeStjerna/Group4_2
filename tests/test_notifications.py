import unittest
from unittest.mock import patch
import smtplib
import sys
import os
from  src.notifications import send_email_notification

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestNotifications(unittest.TestCase):

    @patch("smtplib.SMTP")
    def test_email_notification(self, mock_smtp):
        """
        Tests if emails are sent from the CI server using mock unit tests in order to improve efficiency and safety.
        """
        mock_server = mock_smtp.return_value

        build_id = "858bcd55379dcb9"
        commit_id = "abc123"
        dev_email = "some_dev@example.com"
        build_status = "Success"
        log_content = "abcabc"
        user = "superman"
        branch = "main"
        send_email_notification(build_id, commit_id, dev_email, build_status, log_content, user, branch)

        mock_server.sendmail.assert_called()
        mock_server.quit.assert_called()

        email = mock_server.sendmail.call_args[0]
        sender, receiver, email_content = email

        self.assertEqual(receiver, dev_email)

        self.assertIn(commit_id, email_content)
        self.assertIn(log_content, email_content)


if __name__ == "__main__":
    unittest.main()