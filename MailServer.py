import sys
import imaplib
import email
from email.header import decode_header, make_header
import datetime
import re

class MailServer():
    IMAP_cli = None

    def __init__(self, server):
        self.IMAP_cli = imaplib.IMAP4_SSL(server)

    def login(self, user, password):
        self.IMAP_cli.login(user, password)
    
    def logout(self):
        self.IMAP_cli.close()
        self.IMAP_cli.logout()

    def _decode_message(self, msg):
        # メール本文のデコード
        if msg.is_multipart() is False:
            # シングルパートのとき
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset()
            if charset is not None:
                message = payload.decode(charset, "ignore")
        else:
            # マルチパートのとき
            for part in msg.walk():
                payload = part.get_payload(decode=True)
                if payload is None:
                    continue
                charset = part.get_content_charset()
                if charset is not None:
                    message = payload.decode(charset, "ignore")
        
        return message

    def get_amazon_arriving_estimates(self):
        self.IMAP_cli.select('amazon')

        # まだ確認していない、件名に発送が入っているアマゾンからのメールを抽出
        typ, data = self.IMAP_cli.search(None, f'(SUBJECT "item has shipped" FROM "Amazon.co.jp" NEW)')
        estimates = []
        for num in data[0].split():
            typ, data = self.IMAP_cli.fetch(num, '(RFC822)')
            email_message = email.message_from_bytes(data[0][1])
            message = self._decode_message(email_message)

            # 1通のメールに複数配達日が書いてあるケースを考慮し、配達日毎のまとまりに分割
            arrivings = message.split('Arriving')[1:] # 0個目はヘッダ等なので省く
            for arriving in arrivings:
                description = ''
                # 配達予定の商品を抽出する
                # 商品名 - 販売元……の順で記載されているので、Sold byで分割し、各要素の最後の部分を使う
                solds = arriving.split('Sold by:')[:-1]
                for sold_by in solds:
                    if description != '':
                        description += '\n'
                    # 各まとまりを後ろから商品名周辺のタグで検索し、スライスで商品名を抽出
                    description += sold_by[sold_by.rfind('sans-serif">') + 13:sold_by.rfind('</a>')]

                # 商品名の記載が無ければ追加しない
                if description == '':
                    continue

                # 配達予定日を抽出。大体ここに書いてあるというアタリで取り出す
                estimate_date = re.search(r'\d{2}\/\d{2}', arriving[:50]).group()
                estimates.append((estimate_date, description))

        return estimates
