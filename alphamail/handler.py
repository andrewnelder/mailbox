## I M P O R T S #############################################################


import email
from datetime import datetime

from .imap import ImapTransport


## M A I L B O X   C L A S S #################################################


class MailBox(object):

    def __init__(self, hostname, username=None, password=None, ssl=True):

        server = ImapTransport(hostname, ssl=ssl)
        self.connection = server.connect(username, password)

    def parse_email(self, raw_email, uid):

        email_message = email.message_from_string(raw_email)

        maintype = email_message.get_content_maintype()

        text_body = []
        if maintype == 'multipart':
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    text_body.append(part.get_payload(decode=True))
        elif maintype == 'text':
            text_body.append(email_message.get_payload(decode=True))
        text_body = " ".join(text_body)

        email_dict = dict(email_message.items())
        from_dict = {}
        from_ = email.utils.parseaddr(email_dict['From'])
        if len(from_) == 2:
            from_dict = {'name': from_[0], 'email': from_[1]}

        to_dict = {}
        to_ = email.utils.parseaddr(email_dict['To'])
        if len(to_) == 2:
            to_dict = {'name': to_[0], 'email': to_[1]}

        subject = email_dict.get('Subject', None)
        if subject:
            subject = subject.replace("\n", "").replace("\r", "")

        date = email_dict.get('Date', None)
        message_id = email_dict.get('Message-ID', None)

        # Get the headers
        headers = {}
        headers_keys = ['Received-SPF', 'MIME-Version', 'X-Spam-Status', 'X-Spam-Score']

        for key in headers_keys:
            header_value = email_dict.get(key)
            if header_value:
                headers[key] = header_value

        return {
            'id': uid,
            'msg_id': message_id,
            'from_address': from_dict,
            'to_address': to_dict,
            'subject': subject,
            'date': date,
            'text_body': text_body,
            'headers': headers
        }

    def fetch_message(self, uid):
        _, data = self.connection.uid('fetch', uid, '(RFC822)')
        raw_email = data[0][1]
        email_metadata = self.parse_email(raw_email, uid)
        return email_metadata

    def fetch_messages(self, uids):
        return [self.fetch_message(uid) for uid in uids]

    def get_message_uids(self, msg_status="ALL", msg_from=None, msg_since=None, mailbox=None):

        # select the mailbox - defaults to 'INBOX'
        self.connection.select()
        if mailbox:
            self.connection.select(mailbox)

        # construct the search parameters
        search_parameters = []
        search_parameters.append("({0})".format(msg_status))
        if msg_since:
            if msg_since.lower() == 'today':
                msg_since = datetime.today().strftime('%d-%b-%Y')
            search_parameters.append('(SINCE {0})'.format(msg_since))
        if msg_from:
            search_parameters.append('(FROM "{0}")'.format(msg_from))
        search_parameters_string = ' '.join(search_parameters)

        # perform server request and return a list of uids
        _, uid_string = self.connection.uid('search', None, search_parameters_string)
        return uid_string[0].split()

    def get_all(self, msg_from=None, msg_since=None, mailbox=None):
        uids = self.get_message_uids(msg_status="ALL", msg_from=msg_from, msg_since=msg_since)
        return self.fetch_messages(uids)

    def get_unread(self, msg_from=None, msg_since=None, mailbox=None):
        uids = self.get_message_uids(msg_status="UNSEEN", msg_from=msg_from, msg_since=msg_since)
        return self.fetch_messages(uids)
