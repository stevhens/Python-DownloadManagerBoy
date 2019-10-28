import os, requests
import threading
import urllib.request, urllib.error, urllib.parse
import time

import sys
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow
from PyQt5.uic import loadUi

def start():
    app=QApplication(sys.argv)
    widget=MyDownloadManager()
    widget.show()

    sys.exit(app.exec_())

class MyDownloadManager(QMainWindow):
    def __init__(self):
        super(MyDownloadManager,self).__init__()
        loadUi('downloadmanager.ui', self)
        self.setWindowTitle('Team A Download Manager PyQt5 GUI')

        self.pushButton.clicked.connect(self.on_pushButton_clicked)
    @pyqtSlot()
    def on_pushButton_clicked(self):
        URL = self.url.text()
        splitInto = self.parts.text()
        fileName = self.filename.text()
        self.processLabel.setText('Downloading from: '+ self.url.text())

        main(URL, int(splitInto), fileName)

        sys.exit(app.exec_())

#Test URL
#https://speed.hetzner.de/100MB.bin
#https://cartographicperspectives.org/index.php/journal/article/download/cp50-issue/pdf


# split total num bytes into ranges
def buildRange(value, numsplits):
    lst = []
    for i in range(numsplits):
        chunkSize = value/(numsplits)
        startRange = int(round(1+i * value/(numsplits),0))
        endRange = int(round(startRange-1 + chunkSize, 0))
        if i == 0:
            lst.append('%s-%s' % (i, endRange))
        else:
            lst.append('%s-%s' % (startRange, endRange))
    return lst

def main(url=None, splitBy=8, fileName=None):
    if os.path.exists(fileName):
        print("%s already exists" % fileName)
    else:
        start_time = time.time()
        if not url:
            print("Please Enter some url to begin download.")
            return

        #splitting last / on URL to set as file format
        extension = url.split('/')
        fileName += '.' + extension[-1]

        sizeInBytes = requests.head(url, headers={'Accept-Encoding': 'identity'}).headers.get('content-length', None)
        print(("Downloading file..."))

        if not sizeInBytes:
            print("Size cannot be determined.")
            return

        dataDict = {}
        
        ranges = buildRange(int(sizeInBytes), splitBy)

        def downloadChunk(idx, irange):
            req = urllib.request.Request(url)
            req.headers['Range'] = 'bytes={}'.format(irange)
            dataDict[idx] = urllib.request.urlopen(req).read()

        # create one downloading thread per chunk
        downloaders = [
            threading.Thread(
                target=downloadChunk, 
                args=(idx, irange),
            )
            for idx,irange in enumerate(ranges)
        ]

        # start threads, let run in parallel, wait for all to finish
        for th in downloaders:
            th.start()

        for th in downloaders:
            th.join()

        print(('done: got {} parts, total {} bytes'.format(
            len(dataDict), sum( (
                len(chunk) for chunk in list(dataDict.values())
            ) )
        )))

        print(("--- Time Elapsed: %s seconds ---" % str(time.time() - start_time)))

        if os.path.exists(fileName):
            os.remove(fileName)
        
        # reassemble file in correct order
        with open(fileName, 'wb') as fh:
            for _idx, chunk in sorted(dataDict.items()):
                fh.write(chunk)

        print(("Finished Writing file %s" % fileName))
        print(('file size {} bytes'.format(os.path.getsize(fileName))))

if __name__ == '__main__':
    start()
