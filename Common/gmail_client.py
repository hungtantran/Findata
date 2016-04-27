__author__ = 'hungtantran'


import httplib2
import os
import base64
from email.mime.text import MIMEText

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

from constants_config import Config
import logger

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None


class GmailClient(object):
    SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
    APPLICATION_NAME = 'gmail_client'

    def __init__(self, secret_json, user_id):
        self.secret_json = secret_json
        self.user_id = user_id

        credentials = self.get_credentials(secret_json)
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('gmail', 'v1', http=http)

    def get_credentials(self, secret_json):
        """Gets valid user credentials from storage.

        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.

        Returns:
            Credentials, the obtained credential.
        """
        credential_dir = os.path.join('.credentials')
        if not os.path.exists(credential_dir):
            os.makedirs(credential_dir)
        credential_path = os.path.join(credential_dir, 'secret.json')

        store = oauth2client.file.Storage(credential_path)
        credentials = store.get()
        if not credentials or credentials.invalid:
            flow = client.flow_from_clientsecrets(secret_json, GmailClient.SCOPES)
            flow.user_agent = GmailClient.APPLICATION_NAME
            if flags:
                credentials = tools.run_flow(flow, store, flags)
            else: # Needed only for compatibility with Python 2.6
                credentials = tools.run(flow, store)
        return credentials

    def CreateMessage(self, content, subject, toLine, ccLine=None, bccLine=None):
        """Create a message for an email.

        Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.

        Returns:
        An object containing a base64url encoded email object.
        """
        message = MIMEText(content)
        message['to'] = toLine

        if ccLine is not None:
            message['cc'] = ccLine

        if bccLine is not None:
            message['bcc'] = bccLine

        message['from'] = Config.gmail_client_userid
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_string())}

    def send_mail(self, content, subject, toLine, ccLine=None, bccLine=None):
        """Send an email message.

        Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

        Returns:
        Sent Message.
        """
        try:
            logger.Logger.log(logger.LogLevel.INFO, 'Try sending message with subject %s to %s' % (subject, toLine))
            message = self.CreateMessage(content, subject, toLine, ccLine, bccLine)
            message = (self.service.users().messages().send(userId=self.user_id,
                                                            body=message).execute())
            logger.Logger.log(logger.LogLevel.INFO, 'Sent message id: %s' % message['id'])
            return message
        except Exception as e:
            logger.Logger.log(logger.LogLevel.ERROR, e)


