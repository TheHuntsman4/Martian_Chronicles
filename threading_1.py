from PyQt5.QtCore import QThread, pyqtSignal
from urllib.request import urlopen
class DownloadThread(QThread): 
    
    signal = pyqtSignal('PyQt_PyObject') 

    def __init__(self): 
        QThread.__init__(self) 
        self.photo_list = []

    def run(self):
        
        for i in range(len(self.photo_list)):
            if i == 10: 
                break

            
            res = urlopen(self.photo_list[i]['img_src'])
            # Emit signal when process is over
        self.signal.emit(res.getcode())
        


                #* Threading 
        self.dl_thread = DownloadThread()
        self.dl_thread.signal.connect(self.finished)