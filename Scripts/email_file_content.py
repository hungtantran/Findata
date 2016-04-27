__author__ = 'hungtantran'


import os
import unittest

import logger
from gmail_client import GmailClient
from constants_config import Config


def send_file_content(file, subject, toLine):
    with open(file) as f:
        content = f.read()
        client = GmailClient(secret_json=Config.gmail_secret_json,
                             user_id=Config.gmail_client_userid)

        message = client.send_mail(content=content,
                                   subject=subject,
                                   toLine=toLine,
                                   ccLine=None,
                                   bccLine=None)

if __name__ == '__main__':
    send_file_content(
            file='result.txt',
            subject='Biggest US Software Stocks with Highest Loss Yesterday!',
            toLine='hungtantran@gmail.com,nwickham14@gmail.com')
