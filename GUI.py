from multiprocessing.pool import ThreadPool
from PyQt5 import uic
from PyQt5.QtWidgets import QTextEdit,QMainWindow,QApplication,QPushButton,QLabel,QDialog,QLineEdit,QComboBox,QCalendarWidget,QProgressBar
from PyQt5.QtGui import QImage,QPixmap
from urllib.request import urlopen
import json
from urllib.request import urlretrieve
import sys,os,requests,ezgmail,shutil 
from PyQt5.QtCore import QThread,pyqtSignal
from threading import *
# import env__
# from dotenv import load_dotenv

#Threading the mail

class MailThread(QThread):

    signal = pyqtSignal('PyQt_PyObject')

    def __init(self):
        self.receiver = ""
        self.subject = ""
        self.body = ""

    def run(self):

        image_data=[]
        for file in os.listdir("images"):
            image_data.append(f'images/{file}')
        print(image_data)
             
        try:
            ezgmail.send('{self.receiver}',self.subject,self.body,attachments=image_data)
            code=0
            print("mail sent successfully")
        except:
            code=1

        self.signal.emit(code)
      
#Threading the Downloading stage
class DownloadThread(QThread):

    signal=pyqtSignal('PyQt_PyObject')
    def __init__(self):
        QThread.__init__(self)
        self.pic=[]
    
    def run(self):
        if os.path.exists("images"):
            shutil.rmtree("images")
            os.makedirs("images")
        else:
            os.makedirs("images")
        for i in range(len(self.pic)):
            res=urlopen(self.pic[i]['img_src'])
            if res.getcode()==200:
                with open(f'images/image{i}.png',"wb") as file:
                    file.write(res.read())
            else:
                print("no pics found for this input")
        


#The actual Main window
class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('form.ui', self) # Load the .ui file
        
        self.file=[]
        for filename in os.listdir("images"):
            self.file.append(filename)



        self.i=1
        self.image_urls=[]
        # the next and previous buttons
        self.next=self.findChild(QPushButton,"next")
        self.next.clicked.connect(self.next_pic)
        self.prev=self.findChild(QPushButton,"prev")
        self.prev.clicked.connect(self.prev_pic)
        
        #image fetcher
        self.button=self.findChild(QPushButton,"pushButton")
        self.button.clicked.connect(self.fetcher)  
        self.download_thread=DownloadThread()
        self.download_thread.signal.connect(self.finished)  
        #main label where the images load
        self.label=self.findChild(QLabel,"label")   

        self.mail_button=self.findChild(QPushButton,"one")
        self.mail_button.clicked.connect(self.mailbox_call)

        
        #provides initial cover image
        self.pixmap=QPixmap(f'cover.png')
        self.label.setPixmap(self.pixmap)
        
        #The input combobox for selecting the rover
        self.rover_combo=self.findChild(QComboBox,"comboBox")
        self.rover_combo.addItems(['curiosity','spirit','opportunity'])
        #the calender widget to get dates
        self.calender=self.findChild(QCalendarWidget,"calendarWidget")
        self.calender.selectionChanged.connect(self.selected_date)
        self.inp_date=''

        #jump button
        self.jump=self.findChild(QLineEdit,"jumper")
        self.jump.textChanged.connect(self.image_jump)
        
        self.show() 


   #fuction to get the date 
    def selected_date(self):
        date=self.calender.selectedDate()
        self.inp_date=(str(date.toPyDate()))


   
    #function def of how to load the next image   
    def next_pic(self):
        
        file=self.file
        print(f'{self.i} loaded')
        self.pixmap=QPixmap(f'images/image{self.i}.png')
        self.label.setPixmap(self.pixmap)
        if(self.i<len(file)):
            self.i+=1
        else:
            self.i=1
            self.pixmap=QPixmap(f'cover.png')
            self.label.setPixmap(self.pixmap)
        self.jump.setText(str(self.i))
            
    #function def to load previous image
    def prev_pic(self):
        
        file=self.file
        print(f'{self.i} loaded')
        self.pixmap=QPixmap(f'images/image{self.i}.png')
        self.label.setPixmap(self.pixmap)
        if(self.i>0):
            self.i-=1
        else:
            self.i=1
            self.pixmap=QPixmap(f'cover.png')
            self.label.setPixmap(self.pixmap)
        self.jump.setText(str(self.i))

        
    def image_jump(self):
        try:
            self.i=int(self.jump.text())
            self.pixmap=QPixmap(f'images/image{self.i}.png')
            self.label.setPixmap(self.pixmap)
        except:
            pass
        

        

    #function to get the images
    def fetcher(self):
        

        rover=str(self.rover_combo.currentText())    
        key="QN8PUdf7XPHoSfQptbB7IbrE7nSRkhBqBJDIOLh0"
        date=self.inp_date
        

        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?earth_date={date}&api_key={key}"
        response = urlopen(url) 
        data_json = json.loads(response.read())
        image_urls=[]
        for x in data_json["photos"]:
            image_urls.append(x['img_src'])
        self.image_urls=image_urls
        i=1
        for x in image_urls:
            print(x)
        #starting the thread
        self.download_thread.pic = data_json['photos']
        self.download_thread.start()

    def finished(self):
    
    # Display first image
        self.pixmap = QPixmap(f"images/image0.png")
        self.label.setPixmap(self.pixmap)
    
    
    def mailbox_call(self):
        call=MailDialog(self)
        call.exec()
        self.setWindowTitle(f"Mail sent!")


class MailDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        
        uic.loadUi('mail.ui', self)

        self.to_field = self.findChild(QTextEdit, "textEdit")
        self.subject_field = self.findChild(QTextEdit, "textEdit_2")
        self.body_field = self.findChild(QTextEdit, "textEdit_3")
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
        print(receiver)
        subject = self.subject_field.toPlainText()
        print(subject)
        body = self.body_field.toPlainText()
        print(body)
        self.mail_thread.receiver = receiver
        self.mail_thread.subject = subject
        self.mail_thread.body = body
        
        self.mail_thread.start()

    def sent(self, result):
        if result:
            fail=error_box()
            fail.exec()
        else:
            sucess=it_works()
            sucess.exec()
        
        self.close()

class error_box(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi('email_error.ui', self)
        self.message=self.findChild(QLabel,"label")
        self.ok_button = self.findChild(QPushButton, "pushButton")
        self.ok_button.clicked.connect(lambda:self.close())
        
class it_works(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        uic.loadUi('mail_sent.ui', self)
        self.message=self.findChild(QLabel,"label")
        self.ok_button = self.findChild(QPushButton, "pushButton")
        self.ok_button.clicked.connect(lambda:self.close())

app = QApplication(sys.argv)
window = Ui()
app.exec_()