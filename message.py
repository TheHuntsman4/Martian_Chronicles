import ezgmail
import sys, os, glob
import requests
from urllib.request import urlopen

from PyQt5 import uic
from PyQt5.uic import loadUi
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QLabel, QComboBox, QDateEdit, QDialog, QTextEdit

class DownloadThread(QThread):
    
    signal = pyqtSignal('PyQt_PyObject')

    def __init__(self):
        QThread.__init__(self) 
        self.photo_list = []

    def run(self):
        
        for i in range(len(self.photo_list)):
            if i == 10: # Limit of 10 images
                break

            res = urlopen(self.photo_list[i]['img_src'])
            if res.getcode() == 200:
                with open(f"images/{i}.png", "wb") as file:
                    file.write(res.read())
                
        self.signal.emit(res.getcode())

class MailThread(QThread):

    signal = pyqtSignal('PyQt_PyObject')

    def __init(self):
        self.receiver = ""
        self.subject = ""
        self.body = ""

    def run(self):

        count = 0
        dir_path = r'/home/deny/amFOSS/martian/images'
        for path in os.listdir(dir_path):
            if os.path.isfile(os.path.join(dir_path, path)):
                count += 1

        if "," in self.receiver:
            for address in list(self.receiver.split(",")):
                attachments = [f"images/{i}.png" for i in range(count)]
                try: 
                    ezgmail.send(address, self.subject, self.body, attachments)
                    code = 0
                except:
                    code = 1


        else:
            attachments = [f"images/{i}.png" for i in range(count)]
            try:
                ezgmail.send(self.receiver, self.subject, self.body, attachments)
                code = 0
            except:
                code = 1

        self.signal.emit(code)

# Main Window        
class UI(QMainWindow):
    
    current_image = 0 # Filename without EXT
    last_image = -1 # Var to save final filename without EXT

    def __init__(self):
        super(UI, self).__init__()

        uic.loadUi('base.ui', self)

        self.setWindowTitle("Martian Chronicles")

        self.dropdown = self.findChild(QComboBox, "comboBox")
        self.next_button = self.findChild(QPushButton, "pushButton")
        self.previous_button = self.findChild(QPushButton, "pushButton_2")
        self.fetch_button = self.findChild(QPushButton, "pushButton_4")
        self.mail = self.findChild(QPushButton, "pushButton_3")
        self.date = self.findChild(QDateEdit, "dateEdit")
        self.image = self.findChild(QLabel, "label")

        self.pixmap = QPixmap(f"default.png")
        self.image.setPixmap(self.pixmap)
        self.image.setAlignment(Qt.AlignCenter)

        self.next_button.clicked.connect(self.next)
        self.previous_button.clicked.connect(self.previous)
        self.fetch_button.clicked.connect(self.fetch)
        self.mail.clicked.connect(self.send_mail)

        self.next_button.setEnabled(False)
        self.previous_button.setEnabled(False)
        # self.mail.setEnabled(False)

        
        self.dl_thread = DownloadThread()
        self.dl_thread.signal.connect(self.finished)
        self.dl_thread.photo_list = []
       
        self.show()

    def next(self):

        if os.path.isfile(f"images/{self.current_image + 1}.png"):
            self.current_image += 1
        else:
            self.current_image = 0 
        
        self.pixmap = QPixmap(f"images/{self.current_image}.png")
        self.image.setPixmap(self.pixmap)

        self.setWindowTitle(f"{self.current_image}.png")
    
    def previous(self):

        if os.path.isfile(f"images/{self.current_image - 1}.png"):
            self.current_image -= 1
        else:
            self.current_image = self.last_image
 
        self.pixmap = QPixmap(f"images/{self.current_image}.png")
        self.image.setPixmap(self.pixmap)

        self.setWindowTitle(f"{self.current_image}.png")
    
    def fetch(self):

        self.fetch_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.previous_button.setEnabled(False)
        self.mail.setEnabled(False)
        self.date.setEnabled(False)
        self.dropdown.setEnabled(False)

        files = glob.glob('images/*')
        for f in files:
            os.remove(f)
            
        API_KEY = os.getenv("NASAKEY")

        base_url = "https://api.nasa.gov/mars-photos/api/v1/rovers/"
        
        rover = self.dropdown.currentText()
        datetimeDate = self.date.date().toPyDate()
        date = datetimeDate.strftime('%Y-%m-%d')

        url = base_url + rover.lower() + "/photos?"
        parameters = {
            "earth_date": date,
            "api_key": "ht4THB6YMyQS61KUTjWOCXCTcGXOA15k7Aalx7rt"
        }

        response = requests.get(url, params=parameters)

        if list(str(response.status_code))[0] != "2":
            self.fetch_button.setEnabled(True)
            self.date.setEnabled(True)
            self.dropdown.setEnabled(True)
            
            server_error_dlg = ServerErrorDialog()
            server_error_dlg.exec()

            return

        elif response.json()['photos'] == []:
            self.fetch_button.setEnabled(True) 
            self.date.setEnabled(True)
            self.dropdown.setEnabled(True)

            no_photos_dlg = PhotoErrorDialog()
            no_photos_dlg.exec()

            return

        self.dl_thread.photo_list = response.json()['photos']
        
        self.last_image = len(self.dl_thread.photo_list) - 1
        if self.last_image > 9:
            self.last_image = 9
        
        self.setWindowTitle('Downloading Images...')
        
        self.dl_thread.start()


    def finished(self, result):
        
        self.pixmap = QPixmap(f"images/0.png")
        self.image.setPixmap(self.pixmap)
        self.setWindowTitle(f"0.png")

        self.fetch_button.setEnabled(True)
        self.next_button.setEnabled(True)
        self.previous_button.setEnabled(True)
        self.mail.setEnabled(True)
        self.date.setEnabled(True)
        self.dropdown.setEnabled(True)

    def send_mail(self):
        dlg = MailDialog(self)
        dlg.exec()

        self.setWindowTitle(f"Mail sent!")


class MailDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        loadUi('mail.ui', self)

        self.to_field = self.findChild(QTextEdit, "textEdit")
        self.subject_field = self.findChild(QTextEdit, "textEdit_3")
        self.body_field = self.findChild(QTextEdit, "textEdit_2")
        self.send_mail = self.findChild(QPushButton, "pushButton")
        self.cancel = self.findChild(QPushButton, "pushButton_2")

        self.send_mail.clicked.connect(self.send)
        self.cancel.clicked.connect(lambda:self.close())

        self.mail_thread = MailThread()
        self.mail_thread.signal.connect(self.sent)

        self.setWindowTitle(f"Mail")

    def send(self):
        
        self.send_mail.setEnabled(False)
        self.cancel.setEnabled(False)
        self.to_field.setEnabled(False)
        self.subject_field.setEnabled(False)
        self.body_field.setEnabled(False)
        
        self.setWindowTitle("Sending mail...")

        receiver = self.to_field.toPlainText()
        subject = self.subject_field.toPlainText()
        body = self.body_field.toPlainText()

        self.mail_thread.receiver = receiver
        self.mail_thread.subject = subject
        self.mail_thread.body = body
        
        self.mail_thread.start()

    def sent(self, result):
        if result:
            failure = EmailError()
            failure.exec()
        else:
            sucess = EmailSent()
            sucess.exec()
        
        self.close()

class ServerErrorDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi('server_error.ui', self)
    
        self.ok_button = self.findChild(QPushButton, "pushButton")

        self.ok_button.clicked.connect(lambda:self.close())

class PhotoErrorDialog(QDialog):
    
    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi('no_photos.ui', self)

        self.ok_button = self.findChild(QPushButton, "pushButton")

        self.ok_button.clicked.connect(lambda:self.close())

class EmailError(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi('email_error.ui', self)
    
        self.ok_button = self.findChild(QPushButton, "pushButton")

        self.ok_button.clicked.connect(lambda:self.close())
        
class EmailSent(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        loadUi('mail_sent.ui', self)
    
        self.ok_button = self.findChild(QPushButton, "pushButton")

        self.ok_button.clicked.connect(lambda:self.close())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    UIWindow = UI()
    app.exec_()

#* Dates with images and dates without
# With:
# Curiosity 03-06-2015
#           03-07-2015
# Without:
# Spirit 03-06-2015