#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import hashlib
import sys
import urllib.parse as urlparse
from pathlib import Path
from urllib.parse import parse_qs
import lxml.html as lh
import requests
from bs4 import BeautifulSoup
import smtplib, ssl
from email.message import EmailMessage
from unidecode import unidecode


# Settings for icms
icms_username = ''
icms_password = ''

# Settings for Telegram
telegram_bot_token = '****'
telegram_chatID = '****'

# Settings for Mail
port = 465  # For SSL
smtp_server = ""
user = ""
password = ""
sender_email = ""
receiver_email = ""

# Define and create (empty) helper hash file
hashfile = "examcheck.txt"
open(hashfile, 'a').close()


def mail_sendtext(mail_message, course):
    msg = EmailMessage()
    msg.set_content(mail_message)
    msg['Subject'] = "Es gibt Änderungen beim Notenspiegel: {}".format(course)
    msg['From'] = "Noten-Bot <{}>".format(sender_email)
    msg['To'] = receiver_email

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(user, password)
        # server.sendmail(sender_email, receiver_email, msg)
        server.send_message(msg)


def telegram_bot_sendtext(bot_message):
    send_text = 'https://api.telegram.org/bot' + telegram_bot_token + '/sendMessage?chat_id=' \
                + telegram_chatID + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)
    return response.json()


def get_icms_data():
    payload = {
        "asdf": icms_username,
        "fdsa": icms_password,
        "name": "submit"
    }

    session_requests = requests.session()
    session_requests.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'})

    login_url = "https://icms.hs-hannover.de/qisserver/rds?state=user&type=0"
    print("Rufe Startseite auf")
    result = session_requests.get(login_url)

    # login...
    print("Einloggen...")
    url_loginPost = "https://icms.hs-hannover.de/qisserver/rds?state=user&type=1&category=auth.login&startpage=portal.vm"
    result = session_requests.post(
        url_loginPost,
        data=payload
    )

    # Extract SessionID
    asi = None

    soup = BeautifulSoup(str(result.content), 'html.parser')
    for link in soup.find_all('a'):
        parsed = urlparse.urlparse(link.get('href'))
        params = parse_qs(parsed.query)
        if "asi" in params:
            asi = params.get("asi")[0]

    if asi is None:
        print("SessionID couldn't be extracted")
        sys.exit()

    print("Rufe Notenuebersicht Seite auf...")
    return session_requests.get(
        "https://icms.hs-hannover.de/qisserver/rds?state=notenspiegelStudent&next=list.vm&nextdir=qispos/notenspiegel/student&createInfos=Y&struct=auswahlBaum&nodeID=auswahlBaum%7Cabschluss%3Aabschl%3D84%2Cstgnr%3D1&expand=0&asi=" + asi,
        headers=dict(referer="https://icms.hs-hannover.de/qisserver/rds?state=sitemap&topitem=leer&breadCrumbSource=portal")
    )


def extract_grades_from_html():
    result = get_icms_data()
    doc = lh.fromstring(str(result.content))
    table_elements = doc.xpath('//table')
    notenuebersicht_table = table_elements[1]

    f_noten = {}

    for tr in notenuebersicht_table:
        i = 0
        pruefungsnr = 0
        pruefungstext = 0
        art = 0
        note = 0
        status = 0
        credits = 0
        semester = 0
        for td in tr:
            text = str(td.text.replace("\\xc3\\xbc", "ü").replace("\\t", "").replace("\\r", "").replace("\\n", "").strip())

            i = i + 1
            if i == 1:
                pruefungsnr = text
            if i == 2:
                pruefungstext = text
            if i == 3:
                art = text
            if i == 4:
                note = text
            if i == 5:
                status = text
            if i == 7:
                credits = text
            if i == 9:
                semester = text

        if art != "PL":
            continue

        if semester not in f_noten:
            f_noten[semester] = dict()
        f_noten[semester][pruefungsnr] = {
            'pruefungstext': pruefungstext,
            'note': note,
            'status': status,
            'credits': int(credits)
        }
    return f_noten


def do_action(course, status, grade):
    message = 'Neuer Pruefungsstatus\n'
    message += "\nModul: " + course + \
      "\nStatus: " + status + \
      "\nNote: " + grade
    #telegram_bot_sendtext(message)
    mail_sendtext(unidecode(message), unidecode(course))


def check_for_new(noten):
    for semester in noten:
        for pruefungsnr in noten[semester]:
            toHash = semester + pruefungsnr + noten[semester][pruefungsnr]["status"]
            hash = hashlib.md5(toHash.encode("UTF-8")).hexdigest()

            knownHashes = Path(hashfile).read_text()
            f = open(hashfile, 'a+')
            if hash not in knownHashes:
                f.write(hash + "\n")
                do_action(noten[semester][pruefungsnr]["pruefungstext"], noten[semester][pruefungsnr]["status"], noten[semester][pruefungsnr]["note"])
            f.close()

check_for_new(extract_grades_from_html())
