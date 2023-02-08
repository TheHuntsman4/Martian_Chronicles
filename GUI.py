from multiprocessing.pool import ThreadPool
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QPushButton,QLabel,QDialog,QLineEdit,QComboBox,QCalendarWidget
from PyQt5.QtGui import QImage,QPixmap
from urllib.request import urlopen
import json
from urllib.request import urlretrieve
import sys,os,requests,ezgmail,shutil 
from PyQt5.QtCore import QThread,pyqtSignal

class mailbox(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('mailbox.ui',self)
        
        self.To=self.findChild(QLineEdit,"To")
        self.subject=self.findChild(QLineEdit,"Subject")
        self.Body=self.findChild(QLineEdit,"Body")
        self.send=self.findChild(QPushButton,"send")
        self.send.clicked.connect(self.mail_send)#hook this up with mail_send
    
    def mail_send(self):
        image_data=[]
        for file in os.listdir("images"):
            image_data.append(f'images/{file}')
        print(image_data)        
        ezgmail.send(self.To.text(),self.subject.text(),self.Body.text(),attachments=image_data)
        print("sending email now")        

        self.show()

        

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
                print("no pics found for this ")
        self.signal.emit(res.getcode())



class Ui(QMainWindow):
    def __init__(self):
        super(Ui, self).__init__() # Call the inherited classes __init__ method
        uic.loadUi('form.ui', self) # Load the .ui file
        
        self.i=0
        # the next and previous buttons
        self.next=self.findChild(QPushButton,"next")
        self.next.clicked.connect(self.next_pic)
        self.prev=self.findChild(QPushButton,"prev")
        self.prev.clicked.connect(self.prev_pic)
        
        #image fetcher
        self.button=self.findChild(QPushButton,"pushButton")
        self.button.clicked.connect(self.fetcher)  
        self.dl_thread=DownloadThread()
        self.dl_thread.signal.connect(self.finished)  
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
        
        self.show() 


   #fuction to get the date 
    def selected_date(self):
        date=self.calender.selectedDate()
        self.inp_date=(str(date.toPyDate()))


   
    #function def of how to load the next image   
    def next_pic(self):
        
        file=[]
        for filename in os.listdir("images"):
            file.append(filename)
        print(f'{self.i} loaded')
        self.pixmap=QPixmap(f'images/image{self.i}.png')
        self.label.setPixmap(self.pixmap)
        if(self.i<=len(file)):
            self.i+=1
        else:
            self.pixmap=QPixmap(f'cover.png')
            self.label.setPixmap(self.pixmap)
            
    #function def to load previous image
    def prev_pic(self):
        
        print(f'{self.i} loaded')
        file=[]
        for filename in os.listdir("images"):
            file.append(filename)
        self.pixmap=QPixmap(f'images/image{self.i}.png')
        self.label.setPixmap(self.pixmap)
        if(self.i>0):
            self.i-=1
        else:
            self.pixmap=QPixmap(f'cover.png')
            self.label.setPixmap(self.pixmap)

        

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
        i=1
        for x in image_urls:
            print(x)



        self.dl_thread.pic = data_json['photos']
        self.dl_thread.start()

    def finished(self):
    
    # Display first image
        self.pixmap = QPixmap(f"images/image0.png")
        self.label.setPixmap(self.pixmap)
        
    def mailbox_call(self):
        self.mailbox = mailbox()
        self.mailbox.show()
           


         



app = QApplication(sys.argv)
window = Ui()
app.exec_()