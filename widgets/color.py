#=============================================================================
#%% Color Picker
#=============================================================================
from qt_imports import *
import os

class colorpicker(QWidget):
    """
About:
-----------------
This is a color WIDGET that is like the tkinter one.
It is built to be more keybord friendly.

Use:
-----------------
You use the colorpicker as a normal widget.
Its varibles
colorpicker.name = str of rgb color: '#ff0000'
colorpicker.r>
colorpicker.g>> RGB : r,g,b : 255,0,0
colorpicker.b>
are how you get colors from the widget.
"""
    def __init__(self):

        super(colorpicker,self).__init__()
        hl = QHBoxLayout()
        self.stack = QStackedWidget()
        b = QPushButton('<<>>')
        b.clicked.connect(self.changeStack)
        hl.addWidget(self.stack)
        hl.addWidget(b)
        self.setLayout(hl)
        self.selectorstart()
        self.paletteSelector()
        self.stack.setCurrentIndex(0)


    def selectorstart(self):
        l = QVBoxLayout()
        self.setWindowTitle("Color Dialog")
        self.rline = QGraphicsScene()
        self.rview = QGraphicsView()
        self.rview.setScene(self.rline)
        self.rslider = QSlider(Qt.Horizontal)
        self.rslider.setMinimum(0)
        self.rslider.setMaximum(255)
        self.connect(self.rslider,SIGNAL("sliderMoved(int)"),self.rupdatecolors)
        self.connect(self.rslider,SIGNAL("valueChanged(int)"),self.rupdatecolors)
        #self.setcolors()
        self.gline = QGraphicsScene()
        self.gview = QGraphicsView()
        self.gview.setScene(self.gline)
        self.gslider = QSlider(Qt.Horizontal)
        self.gslider.setMinimum(0)
        self.gslider.setMaximum(255)
        self.connect(self.gslider,SIGNAL("sliderMoved(int)"),self.gupdatecolors)
        self.connect(self.gslider,SIGNAL("valueChanged(int)"),self.gupdatecolors)

        #self.setcolors()
        self.bline = QGraphicsScene()
        self.bview = QGraphicsView()
        self.bview.setScene(self.bline)
        self.bslider = QSlider(Qt.Horizontal)
        self.bslider.setMinimum(0)
        self.bslider.setMaximum(255)
        self.connect(self.bslider,SIGNAL("sliderMoved(int)"),self.bupdatecolors)
        self.connect(self.bslider,SIGNAL("valueChanged(int)"),self.bupdatecolors)
        l.addWidget(self.rview)
        l.addWidget(self.rslider)
        l.addWidget(self.gview)
        l.addWidget(self.gslider)
        l.addWidget(self.bview)
        l.addWidget(self.bslider)
        #**********************
        #valueChanged (int)
        self.r = 0
        self.b = 0
        self.g = 0
        nl = QVBoxLayout()
        self.rspin = QSpinBox()
        self.rspin.setReadOnly(False)
        self.rspin.setMaximum(255)
        self.connect(self.rspin,SIGNAL("valueChanged(int)"),self.update)

        self.gspin = QSpinBox()
        self.gspin.setReadOnly(False)
        self.gspin.setMaximum(255)
        self.connect(self.gspin,SIGNAL("valueChanged(int)"),self.update)

        self.bspin = QSpinBox()
        self.bspin.setReadOnly(False)
        self.bspin.setMaximum(255)
        self.connect(self.bspin,SIGNAL("valueChanged(int)"),self.update)
        self.namebox = QLineEdit()
        self.namebox.setReadOnly(False)
        self.connect(self.namebox,SIGNAL("editingFinished()"),self.setnamed)
        nl.addWidget(self.rspin)
        nl.addWidget(self.gspin)
        nl.addWidget(self.bspin)
        nl.addWidget(self.namebox)

        #************************
        labl = QVBoxLayout()
        rl = QLabel('Red:')
        gl = QLabel('Green:')
        bl = QLabel('Blue:')
        to = QLabel('Color:')
        labl.addWidget(rl)
        labl.addWidget(gl)
        labl.addWidget(bl)
        labl.addWidget(to)
        self.colorbox = QGraphicsView()
        self.incolor = QGraphicsScene()
        self.colorbox.setScene(self.incolor)
        l.addWidget(self.colorbox)
        #ml = QHBoxLayout(self)
        ml = QHBoxLayout()
        ml.addLayout(labl)
        ml.addLayout(l)
        ml.addLayout(nl)

        w = QWidget(self)
        w.setLayout(ml)
        self.stack.addWidget(w)
        self.setcolors(0,0,0)

    def setcolors(self,r,g,b):
        #manargs.check([r,g,b],[int,int,int])
        self.rline.clear()
        self.gline.clear()
        self.bline.clear()
        self.r = r
        self.g = g
        self.b = b
        w = 5
        h = 20
        x = 0
        y = 0
        c = 0
        for i in range(32):
            rcolor = QColor(c,g,b)
            #color.setNamedColor('#ff00ff')
            brush = QBrush(rcolor,Qt.SolidPattern)

            rec = self.rline.addRect(x,y,w,h,rcolor,brush)
            x += 5
            c+=7

        c = 0
        for i in range(32):
            gcolor = QColor(r,c,b)
            #color.setNamedColor('#ff00ff')
            brush = QBrush(gcolor,Qt.SolidPattern)

            rec = self.gline.addRect(x,y,w,h,gcolor,brush)
            x += 5
            c+=7

        c = 0
        for i in range(32):
            bcolor = QColor(r,g,c)
            #color.setNamedColor('#ff00ff')
            brush = QBrush(bcolor,Qt.SolidPattern)

            rec = self.bline.addRect(x,y,w,h,bcolor,brush)
            x += 5
            c+=7

        mcolor = QColor(r,g,b)
        brush = QBrush(mcolor,Qt.SolidPattern)

        self.incolor.addRect(0,0,50,50,mcolor,brush)
        self.name = mcolor.name()

        self.namebox.setText(mcolor.name())


    def rupdatecolors(self,r):
        self.r = r
        self.rspin.setValue(r)
        self.setcolors(r,self.g,self.b)
    def gupdatecolors(self,g):
        self.g = g
        self.gspin.setValue(g)
        self.setcolors(self.r,g,self.b)

    def bupdatecolors(self,b):
        self.b = b
        self.bspin.setValue(b)
        self.setcolors(self.r,self.g,b)

    def update(self,dummy):
        self.r = self.rspin.value()
        self.g = self.gspin.value()
        self.b = self.bspin.value()
        self.rslider.setValue(self.r)
        self.gslider.setValue(self.g)
        self.bslider.setValue(self.b)
        self.setcolors(self.r,self.g,self.b)

    def setnamed(self):
        txt = self.namebox.text()
        self.setNamedColor(txt)

    def setNamedColor(self,color):
        #manargs.check([color],[str])
        r,g,b = HTMLColorToRGB(color)
        self.rslider.setValue(r)
        self.gslider.setValue(g)
        self.bslider.setValue(b)
        self.setcolors(r,g,b)

    def changeStack(self):
        index = self.stack.currentIndex()
        if index == 1:
            self.stack.setCurrentIndex(0)
        else:
            self.stack.setCurrentIndex(1)

    def paletteSelector(self):
        self.palettes = ScopePyPalettes()
        l = QVBoxLayout()
        names = []
        for i in self.palettes.PaletteDict:
            names.append(i)
        self.combo = QComboBox()
        self.combo.addItems(names)
        self.connect(self.combo,SIGNAL("currentIndexChanged(int)"),self.changeColors)
        self.colors = QListWidget()
        print(names)
        bcn = None
        c = 0
        for i in names:
            if i == "BasicColors":

                bcn = c

            if bcn != None:

                c+= 1

        self.combo.setCurrentIndex(bcn)
        allcols = self.palettes.PaletteDict['BasicColors'].getAllColors()
        self.colors.addItems(allcols)
        p1 = QPushButton('Add New Palette!')
        p2 = QPushButton('Add New Color!')
        p3 = QPushButton('Set Selector Color!')
        p4 = QPushButton('Refresh!')
        p4.clicked.connect(self.refresh)
        p2.clicked.connect(self.newColor)
        p1.clicked.connect(self.newPalette)
        p3.clicked.connect(self.setSelectorColor)
        l.addWidget(self.combo)
        l.addWidget(self.colors)
        l.addWidget(p1)
        l.addWidget(p2)
        l.addWidget(p3)
        l.addWidget(p4)
        w = QWidget()
        w.setLayout(l)
        self.stack.addWidget(w)

    def changeColors(self,index):
        c = 0
        self.palettes.refresh()
        a = []
        for i in self.palettes.PaletteDict:
            a.append(i)
            c += 1

        self.colors.clear()
        allcols = self.palettes.PaletteDict[a[index]].getAllColors()
        self.colors.addItems(allcols)

    def refresh(self):
        self.combo.clear()
        names = []
        print(self.palettes.PaletteDict)

        for i in self.palettes.PaletteDict:
            names.append(i)
        print(names)
        self.combo.addItems(names)
        index = self.combo.currentIndex()
        self.changeColors(index)

    def newPalette(self):
        name,dummy = QInputDialog.getText(self,'QInputDialog.getText','Enter the name of your new palette')
        text = self.combo.currentText()
        palette = Palette()
        self.palettes.addPalette(name,palette)
        palette.save(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin',name))
        self.refresh()

    def newColor(self):
        name,dummy = QInputDialog.getText(self,'QInputDialog.getText','Enter the name of your new color')
        text = self.combo.currentText()
        palette = self.palettes.PaletteDict[text]
        print(palette)
        palette.addColor(name,self.name)
        palette.save(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin',text))
        self.refresh()

    def setSelectorColor(self):
        colurs2 = self.colors.selectedItems()
        colorname = colurs2[0].text()
        text = self.combo.currentText()
        palette = self.palettes.PaletteDict[text]
        rgbcolor = palette.getColor(colorname)
        color = rgb_to_hex(rgbcolor)
        self.setNamedColor(color)





def HTMLColorToRGB(colorstring):
    # from stack overflow
    """ convert #RRGGBB to an (R, G, B) tuple """
    colorstring = colorstring.strip()
    if colorstring[0] == '#': colorstring = colorstring[1:]
    if len(colorstring) != 6:
        raise ValueError("input #%s is not in #RRGGBB format" % colorstring)
    r, g, b = colorstring[:2], colorstring[2:4], colorstring[4:]
    r, g, b = [int(n, 16) for n in (r, g, b)]
    return (r, g, b)


    for i in range(len(re)):
        re[i] = uniformLength(re[i])
    return re




import pickle
class Palette:
    """
    Made for ScopePy.
    A way of storing colors
    """
    def __init__(self):
        self._colorDict = {}

    def addColor(self,name,*args):
        """
        Name: Name of color
        Args Can be R, G, B or #RRGGBB
        """
        if isinstance(args[0],str):
            print('string!')
            color = HTMLColorToRGB(args[0])
        else:
            print('not string:',args)
            color = (args[0],args[1],args[2])

        self._colorDict[name]=color

    def deleteColor(self,name):
        self._colorDict.pop(name)

    def getColor(self,name):
        """
        In R, G, B format
        """
        return self._colorDict[name]

    def getAllColors(self):
        names = []
        for i in self._colorDict:
            names.append(i)

        return names
    def save(self,filename):
        f = open(filename,'wb')
        pickle.dump(self._colorDict,f)
        f.flush()
        f.close()

    def load(self,filename):
        f = open(filename,'rb')
        data = pickle.load(f)
        f.close()
        rp = Palette()
        rp._colorDict = data
        return rp

class ScopePyPalettes:
    def __init__(self):
        self.worker = Palette()
        self.PaletteDict = {}
        try:
            ex = self.worker.load(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin','BasicColors'))
        except:
            print('Cannot find Standard Palette: Creating a new one')
            if not os.path.exists(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin')):
                os.mkdir(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin'))
            ex = Palette()
            ex.addColor('Red','#ff0000')
            ex.addColor('Green','#00ff00')
            ex.addColor('Blue','#0000ff')
            ex.addColor('Purple','#9300ff')
            ex.addColor('Yellow','#ffff41')
            ex.addColor('Pink','#ffa6ff')
            ex.addColor('Orange','#ffbc7c')
            ex.addColor('Brown','#b16a2d')
            ex.addColor('White','#ffffff')
            ex.addColor('Black','#000000')
            ex.save(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin','BasicColors'))


        #self.PaletteDict['Basic Colors']=ex
        for i in os.listdir(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin')):
            ex = self.worker.load(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin',i))
            name,path = os.path.split(os.path.join(os.path.expanduser('~'),'.ScopePy','Palette-Bin',i))
            self.PaletteDict[path] = ex

    def addPalette(self,name,palette):
        #manargs.check([palette],[Palette])
        self.PaletteDict[name] = palette

    def refresh(self):
        self.PaletteDict

    def deletePalette(self,name):
        self.PaletteDict.pop(name)


    def getPalette(self,name):
        return self.PaletteDict[name]


def rgb_to_hex(rgb):
   return '#%02x%02x%02x' % rgb

"""
Basic Colors:
Red:#ff0000
Green:#00ff00
blue:#0000ff
Purple:#9300ff
Yellow:#ffff41
Pink:#ffa6ff
orange:#ffbc7c
brown:#b16a2d
black:#000000
white:#ffffff
"""
