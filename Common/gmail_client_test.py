__author__ = 'hungtantran'


import os
import unittest

import logger
from gmail_client import GmailClient
from constants_config import Config


class TestGmailClient(unittest.TestCase):
    def test_send_mail(self):
        client = GmailClient(secret_json=Config.gmail_secret_json,
                             user_id=Config.gmail_client_userid)

        message = client.send_mail('Hello World', 'Hello', Config.gmail_client_userid, None, None)

        self.assertIsNotNone(message)
        self.assertTrue('id' in message)
        self.assertTrue('threadId' in message)
        self.assertTrue('labelIds' in message)


if __name__ == '__main__':
    unittest.main()
