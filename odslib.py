import xml.etree.ElementTree as ET
import zipfile
def load(filename):
    zf = zipfile.ZipFile(filename)
    f = zf.open('content.xml')
    txt = f.read().decode()
    #print(txt)
    f.close()
    zf.close()
    return ODS(txt)

class ODS(object):
    def __init__(self,content):
        self.root = ET.fromstring(content)
        self.body = self.root[3]
        self.spread = self.body[0]
        self.data = self.read()
    def get(self,sheetname,col,row):
        return self.data[sheetname][col][row]
        

    def read(self):
        sheets = {}
        for ch in self.spread:
            try:
                #print(ch.attrib)
                sheetname = ch.attrib['{urn:oasis:names:tc:opendocument:xmlns:table:1.0}name']
            except Exception as ec:
                pass
            #print(sheetname)
            ## To Stop Un Wanted Activity:
            if sheetname in list(sheets.keys()): break
            lta = []
            for row in ch:
                l = []
                for cell in row:
                    #print(cell.tag,cell.attrib,cell.text)
                    try:
                        valtype = cell.attrib['{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value-type']
                        if valtype == 'string':
                            val = cell[0].text
                        else:
                            val = cell.attrib['{urn:oasis:names:tc:opendocument:xmlns:office:1.0}value']
                        
                    except Exception as ec:
                        
                        print(ec.__class__.__name__)
                        print(ec)
                    try:
                        #print(val)
                        if valtype == 'float':
                            val = float(val)
                        else:
                            val = str(val)
                        #print(val)
                    except Exception as ec:
                        print(ec.__class__.__name__)
                        print(ec)
                    #print(val)
                    l.append(val)
                    #print(l)
                lta.append(l)
                #print(lta)
            #lta.pop(0)
            lta.pop(0)
            sheets[sheetname] = lta
        return sheets
        

                        
                    
