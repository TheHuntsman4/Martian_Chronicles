from multiprocessing.pool import ThreadPool
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow,QApplication,QPushButton,QLabel,QDialog,QLineEdit,QComboBox
from PyQt5.QtGui import QImage,QPixmap
from urllib.request import urlopen
import json
from urllib.request import urlretrieve
import sys,os
import requests
from PyQt5.QtCore import QThread,pyqtSignal

class DownloadThread(QThread):
    signal=pyqtSignal('PyQt_PyObject')
    def __init__(self):
        QThread.__init__(self)
        self.pic=[]
    
    def run(self):
        for i in range(len(self.pic)):
            if i==10:
                break
            res=urlopen(self.pic[i]['img_src'])
            if res.getcode()==200:
                with open(f'images/{i}.png',"wb") as file:
                    file.write(res.read())
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
        
        #provides initial cover image
        self.pixmap=QPixmap(f'cover.png')
        self.label.setPixmap(self.pixmap)
        
        #The input combobox for selecting the rover
        self.rover_combo=self.findChild(QComboBox,"comboBox")
        self.rover_combo.addItems(['curiosity','spirit','opportunity'])
        
        
        
        self.show() 


   
    #function def of how to load the next image   
    def next_pic(self):
        
        file=[]
        for filename in os.listdir("images2"):
            file.append(filename)
        print(f'{self.i} loaded')
        self.pixmap=QPixmap(f'images2/image{self.i}.png')
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
        for filename in os.listdir("images2"):
            file.append(filename)
        self.pixmap=QPixmap(f'images2/image{self.i}.png')
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
        date="2015-6-3"
        

        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?earth_date={date}&api_key={key}"
        response = urlopen(url) 
        data_json = json.loads(response.read())
        image_urls=[]
        for x in data_json["photos"]:
            image_urls.append(x['img_src'])
        i=1
        for x in image_urls:
            print(x)
        # for image in image_urls:
        #     image_file=requests.get(image).content
        #     with open(f'images/image{i}.png',"wb") as f:
        #         f.write(image_file)
        #         i+=1


        self.dl_thread.pic = data_json['photos']
        self.dl_thread.start()

    def finished(self):
    
    # Display first image
        self.pixmap = QPixmap(f"images/0.png")
        self.image.setPixmap(self.pixmap)
        self.fetch_button.setEnabled(True)

            

#         self.dateEdit = QtWidgets.QDateEdit(parent=self)
#         self.dateEdit.move(250, 400)
#         self.dateEdit.setGeometry(QRect(42, 150, 200, 21))
#         self.dateEdit.setDisplayFormat("yyyy-MM-dd")
#         self.dateEdit.setDate(QtCore.QDate.currentDate())
        
        


app = QApplication(sys.argv)
window = Ui()
app.exec_()