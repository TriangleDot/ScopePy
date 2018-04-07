# -*- coding: utf-8 -*-
"""
Created on Sat May 16 18:51:34 2015

@author: john

Version
==============================================================================
$Revision:: 43                            $
$Date:: 2015-05-23 09:25:13 -0400 (Sat, 2#$
$Author:: john                            $
==============================================================================


ScopePy Preferences
-------------------

Module for handling Preferences for ScopePy
Defines a class for storing preferences and a dialog box for setting them.
The Preferences class is then used by other parts of ScopePy as a central
location.


"""
#==============================================================================
#%% License
#==============================================================================

"""
Copyright 2015 John Bainbridge

This file is part of ScopePy.

ScopePy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ScopePy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ScopePy.  If not, see <http://www.gnu.org/licenses/>.
"""


#==============================================================================
#%% Imports
#==============================================================================

# Standard library
import os,logging
import configparser


# Third party libraries
from qt_imports import *

# My libraries
import ScopePy_keyboard as kbd
from ScopePy_utilities import minidir

#==============================================================================
#%% Logger
#==============================================================================
# create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add do nothing handler
logger.addHandler(logging.NullHandler())

# create console handler and set level to debug
con = logging.StreamHandler()
con.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('[%(asctime)s:%(name)s:%(levelname)s]: %(message)s')

# add formatter to ch
con.setFormatter(formatter)

# add ch to logger
logger.addHandler(con)

#==============================================================================
#%% Constants
#==============================================================================

DEFAULT_PREFS_FILE = os.path.join(os.path.expanduser('~'),'.ScopePy','preferences.ini')

BASEPATH, dummy = os.path.split(os.path.abspath(__file__))

#==============================================================================
#%% Functions
#==============================================================================

def getPathsFromList(ListWidget):
    """
    Extract the lines of text from a QListWidget

    Inputs
    --------
    ListWidget: QListWidget

    Outputs
    --------
    list of paths: list of str

    """

    # Get list of QListWidget items
    nItems = len(ListWidget)


    if nItems == 0:
        return

    list_of_paths = []

    for index in range(nItems):
        list_of_paths.append(ListWidget.item(index).text())

    return list_of_paths



def addPathsToList(ListWidget,list_of_paths):
    """
    Add a list of paths to a QListWidget

    Input
    -------
    list_of_paths : list of str

    """

    if list_of_paths == [] or list_of_paths is None:
        return

    for path in list_of_paths:
        if path:
            ListWidget.addItem(path)


#==============================================================================
#%% Preferences class
#==============================================================================
class Preferences():
    """
    Holds all the Preferences for ScopePy and handles storing and loading

    """


    def __init__(self):

        self.basepath = BASEPATH

        # Paths
        # ============================
        # Panel paths
        self.panelPaths = []

        # Script paths
        self.scriptPaths = []

        # Transformer paths
        self.transformerPaths = []

        # Math functions paths
        self.mathFunctionPaths = []

        # Macro paths
        self.macroPaths = []

        # Data sources path
        self.dataSourcePaths = []

        # Store last path
        self.lastPath = os.path.expanduser('~')

        # Recent files
        # =====================
        self.recentFiles = []

        # Themes
        # ==========================
        self.theme_css = os.path.join(self.basepath,'themes/default/default.css')
        self.theme = 'default'
        self.themePaths = []

        # Preferences location
        # ==========================
        self.prefs_filename = DEFAULT_PREFS_FILE

        # Keyboard shortcuts
        # =========================
        self.keyboard = kbd.makeDefaultKeyboardShortcuts()


    def save(self):
        """
        Save Preferences to default location

        """

        def isListEmpty(a_list):
            return a_list==[] or a_list is None

        # Check existence of saving directory
        # -------------------------------------
        path, filename = os.path.split(self.prefs_filename)

        # Create directory if needed
        if not os.path.exists(path):
            os.makedirs(path,exist_ok=True)


        # Make the preferences file format
        # -----------------------------------
        config = configparser.ConfigParser()

        config['PATHS'] = {}
        if not isListEmpty(self.panelPaths):
            config['PATHS']['PANELS'] = ";".join(self.panelPaths)

        if not isListEmpty(self.scriptPaths):
            config['PATHS']['SCRIPTS'] = ";".join(self.scriptPaths)

        if not isListEmpty(self.transformerPaths):
            config['PATHS']['TRANSFORMERS'] = ";".join(self.transformerPaths)

        if not isListEmpty(self.macroPaths):
            config['PATHS']['MACROS'] = ";".join(self.macroPaths)

        if not isListEmpty(self.dataSourcePaths):
            config['PATHS']['DATASOURCES'] = ";".join(self.dataSourcePaths)

        if not isListEmpty(self.themePaths):
            config['PATHS']['THEMES'] = ";".join(self.themePaths)

        if not isListEmpty(self.mathFunctionPaths):
            config['PATHS']['MATHFUNCTIONS'] = ";".join(self.mathFunctionPaths)

        config['PATHS']['LAST_PATH'] = self.lastPath

        if not isListEmpty(self.recentFiles):
            config['PATHS']['RECENTFILES'] = ";".join(self.recentFiles)

        config['THEME'] = {}
        if self.theme:
            config['THEME']['SELECTED'] = self.theme



        # TODO : add keyboard shortcuts

        # Store the file
        # ----------------
        with open(self.prefs_filename, 'w') as configfile:
            config.write(configfile)



    def load(self,basepath=BASEPATH):
        """
        Load preferences from default location

        """

        self.basepath = basepath

        # Function for reading from config
        def readIfExists(a_dict,key,default=''):
            if key in a_dict:
                return a_dict[key]
            else:
                return default


        # Check file exists
        # --------------------
        if not os.path.exists(self.prefs_filename):
            logger.debug('Preferences: Cannot find preferences file [%s]' % self.prefs_filename)
            return




        logger.debug('Preferences: Loading from preferences file [%s]' % self.prefs_filename)

        # Load file
        # -------------
        config = configparser.ConfigParser()
        out = config.read(self.prefs_filename)

        if not out:
            logger.debug('Preferences:Error with loading preferences file [%s]' % self.prefs_filename)
            return


        # Extract the preferences data
        # -----------------------------
        self.panelPaths = readIfExists(config['PATHS'],'PANELS').split(';')
        self.scriptPaths = readIfExists(config['PATHS'],'SCRIPTS').split(';')
        self.transformerPaths = readIfExists(config['PATHS'],'TRANSFORMERS').split(';')
        self.macroPaths = readIfExists(config['PATHS'],'MACROS').split(';')
        self.themePaths = readIfExists(config['PATHS'],'THEMES').split(';')
        self.mathFunctionPaths = readIfExists(config['PATHS'],'MATHFUNCTIONS').split(';')
        self.lastPath = config['PATHS']['LAST_PATH']
        self.recentFiles = readIfExists(config['PATHS'],'RECENTFILES').split(';')

        if 'THEME' in config:
            self.theme = readIfExists(config['THEME'],'SELECTED','default')





#==============================================================================
#%% Preference dialog class
#==============================================================================

class PreferencesDialog(QDialog):
    """
    ScopePy preferences

    """

    def __init__(self,parent=None,prefs=Preferences()):

        # Initialise base class
        super(PreferencesDialog,self).__init__(parent)

        self.setWindowTitle("ScopePy Preferences")

        # Setup Preferences data
        # ============================

        self.prefs = prefs



        # Setup widgets
        # =========================

        # Panels tab
        self.panelsPath = QLineEdit()
        self.panelsList = QListWidget()
        panelsBrowseButton = QPushButton("Browse...")
        panelsAddButton = QPushButton("Add")
        panelsRemoveButton = QPushButton("Remove")


        # scripts tab
        self.scriptsPath = QLineEdit()
        self.scriptsList = QListWidget()
        scriptsBrowseButton = QPushButton("Browse...")
        scriptsAddButton = QPushButton("Add")
        scriptsRemoveButton = QPushButton("Remove")

        # transformers tab
        self.transPath = QLineEdit()
        self.transList = QListWidget()
        transAddButton = QPushButton("Add")
        transBrowseButton = QPushButton("Browse...")
        transRemoveButton = QPushButton("Remove")

        # maths functions tab
        self.mathsPath = QLineEdit()
        self.mathsList = QListWidget()
        mathsAddButton = QPushButton("Add")
        mathsBrowseButton = QPushButton("Browse...")
        mathsRemoveButton = QPushButton("Remove")


        # macros tab
        self.macroPath = QLineEdit()
        self.macroList = QListWidget()
        macroAddButton = QPushButton("Add")
        macroBrowseButton = QPushButton("Browse...")
        macroRemoveButton = QPushButton("Remove")

        # Themes tab
        self.currentThemePath = QLineEdit()

        #themeDefaultButton = QPushButton("Set to Default theme")

        self.themePath = QLineEdit()
        self.themeList = QListWidget()
        themeAddButton = QPushButton("Add")
        themeBrowseButton = QPushButton("Browse...")
        themeRemoveButton = QPushButton("Remove")


        # OK/Cancel buttons
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        buttonBox.button(QDialogButtonBox.Ok).setDefault(True)

        # Frame to go around tabs
        # Use this to define the size of the dialog
        mainFrame = QFrame()
        mainFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        mainFrame.setLineWidth(3)
        mainFrame.setMinimumSize(QSize(600,300))
        mainFrame.setMaximumSize(QSize(600,500))
        mainFrame.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)

        # Frame to go around buttons
        buttonFrame = QFrame()
        buttonFrame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        buttonFrame.setLineWidth(3)


        # Setup connections
        # ===========================

        # Panel buttons
        self.connect(panelsBrowseButton,SIGNAL("clicked()"),self.browseForPanelPath)
        self.connect(panelsAddButton,SIGNAL("clicked()"),self.addPanelPath)
        self.connect(panelsRemoveButton,SIGNAL("clicked()"),self.removePanelPath)

        # Script buttons
        self.connect(scriptsBrowseButton,SIGNAL("clicked()"),self.browseForScriptPath)
        self.connect(scriptsAddButton,SIGNAL("clicked()"),self.addScriptPath)
        self.connect(scriptsRemoveButton,SIGNAL("clicked()"),self.removeScriptPath)

        # Transformer buttons
        self.connect(transBrowseButton,SIGNAL("clicked()"),self.browseForTransformerPath)
        self.connect(transAddButton,SIGNAL("clicked()"),self.addTransformerPath)
        self.connect(transRemoveButton,SIGNAL("clicked()"),self.removeTransformerPath)


        # Macro buttons
        self.connect(macroBrowseButton,SIGNAL("clicked()"),self.browseForMacroPath)
        self.connect(macroAddButton,SIGNAL("clicked()"),self.addMacroPath)
        self.connect(macroRemoveButton,SIGNAL("clicked()"),self.removeMacroPath)

        # Maths buttons
        self.connect(mathsBrowseButton,SIGNAL("clicked()"),self.browseForMathFunctionPath)
        self.connect(mathsAddButton,SIGNAL("clicked()"),self.addMathFunctionPath)
        self.connect(mathsRemoveButton,SIGNAL("clicked()"),self.removeMathFunctionPath)

        # Theme buttons
        self.connect(themeBrowseButton,SIGNAL("clicked()"),self.browseForThemePath)
        #self.connect(themeDefaultButton,SIGNAL("clicked()"),self.setDefaultThemePath)
        self.connect(themeAddButton,SIGNAL("clicked()"),self.addThemePath)
        self.connect(themeRemoveButton,SIGNAL("clicked()"),self.removeThemePath)

        # Exit buttons
        self.connect(buttonBox,SIGNAL("accepted()"),self.exitDialog)
        self.connect(buttonBox,SIGNAL("rejected()"),self,SLOT("reject()"))


        # Layout the dialog
        # ==============================

        # Tab widget for different preferences categories
        prefsTab = QTabWidget()


        # Panels tab
        # ------------------------------------------
        panelsLayout = QGridLayout()

        row=0
        panelsLayout.addWidget(QLabel("Add/Remove paths where Panel classes are stored"),row,0)
        row+=1
        panelsLayout.addWidget(self.panelsPath,row,0)
        panelsLayout.addWidget(panelsBrowseButton,row,1)
        row+=1
        # Col 0, rows 1-3
        panelsLayout.addWidget(self.panelsList,row,0,3,1)
        panelsLayout.setColumnStretch(0,3)

        # Col 1, row 1
        panelsLayout.addWidget(panelsAddButton,row,1,1,1)
        row+=1
        # Col 1, row 2
        panelsLayout.addWidget(panelsRemoveButton,row,1,1,1)
        # Col 1, row 3


        panelsWidget = QWidget()
        panelsWidget.setLayout(panelsLayout)

        prefsTab.addTab(panelsWidget,"Panels paths")


        # Scripts tab
        # ------------------------------------------
        scriptsLayout = QGridLayout()

        row=0
        scriptsLayout.addWidget(QLabel("Add/Remove paths where Scripts are stored"),row,0)
        row+=1
        scriptsLayout.addWidget(self.scriptsPath,row,0)
        scriptsLayout.addWidget(scriptsBrowseButton,row,1)
        row+=1
        # Col 0, rows 1-3
        scriptsLayout.addWidget(self.scriptsList,row,0,3,1)
        scriptsLayout.setColumnStretch(0,3)

        # Col 1, row 1
        scriptsLayout.addWidget(scriptsAddButton,row,1,1,1)
        row+=1
        # Col 1, row 2
        scriptsLayout.addWidget(scriptsRemoveButton,row,1,1,1)
        # Col 1, row 3


        scriptsWidget = QWidget()
        scriptsWidget.setLayout(scriptsLayout)

        prefsTab.addTab(scriptsWidget,"Scripts paths")


        # trans tab
        # ------------------------------------------
        transLayout = QGridLayout()

        row=0
        transLayout.addWidget(QLabel("Add/Remove paths where transformer classes are stored"),row,0)
        row+=1
        transLayout.addWidget(self.transPath,row,0)
        transLayout.addWidget(transBrowseButton,row,1)
        row+=1
        # Col 0, rows 1-3
        transLayout.addWidget(self.transList,row,0,3,1)
        transLayout.setColumnStretch(0,3)

        # Col 1, row 1
        transLayout.addWidget(transAddButton,row,1,1,1)
        row+=1
        # Col 1, row 2
        transLayout.addWidget(transRemoveButton,row,1,1,1)
        # Col 1, row 3


        transWidget = QWidget()
        transWidget.setLayout(transLayout)

        prefsTab.addTab(transWidget,"Transformer paths")


        # maths function tab
        # ------------------------------------------
        mathsLayout = QGridLayout()

        row=0
        mathsLayout.addWidget(QLabel("Add/Remove paths where Maths functions are stored"),row,0)
        row+=1
        mathsLayout.addWidget(self.mathsPath,row,0)
        mathsLayout.addWidget(mathsBrowseButton,row,1)
        row+=1
        # Col 0, rows 1-3
        mathsLayout.addWidget(self.mathsList,row,0,3,1)
        mathsLayout.setColumnStretch(0,3)

        # Col 1, row 1
        mathsLayout.addWidget(mathsAddButton,row,1,1,1)
        row+=1
        # Col 1, row 2
        mathsLayout.addWidget(mathsRemoveButton,row,1,1,1)
        # Col 1, row 3


        mathsWidget = QWidget()
        mathsWidget.setLayout(mathsLayout)

        prefsTab.addTab(mathsWidget,"Maths function paths")


        # Macro tab
        # ------------------------------------------
        macroLayout = QGridLayout()

        row=0
        macroLayout.addWidget(QLabel("Add/Remove paths where Macro scripts are stored"),row,0)
        row+=1
        macroLayout.addWidget(self.macroPath,row,0)
        macroLayout.addWidget(macroBrowseButton,row,1)
        row+=1
        # Col 0, rows 1-3
        macroLayout.addWidget(self.macroList,row,0,3,1)
        macroLayout.setColumnStretch(0,3)

        # Col 1, row 1
        macroLayout.addWidget(macroAddButton,row,1,1,1)
        row+=1
        # Col 1, row 2
        macroLayout.addWidget(macroRemoveButton,row,1,1,1)
        # Col 1, row 3


        macroWidget = QWidget()
        macroWidget.setLayout(macroLayout)

        prefsTab.addTab(macroWidget,"Macro paths")


        # Themes tab
        # -------------------
        themeLayout = QGridLayout()
#        themeLayout.addWidget(QLabel('<H2><b>Themes</b></H2>'))
#        themeLayout.addWidget(self.currentThemePath)
#        themeLayout.addWidget(themeBrowseButton)
#        themeLayout.addWidget(themeDefaultButton)

        row=0
        themeLayout.addWidget(QLabel("Add/Remove paths where Themes are stored"),row,0)
        row+=1
        themeLayout.addWidget(self.themePath,row,0)
        themeLayout.addWidget(themeBrowseButton,row,1)
        row+=1
        # Col 0, rows 1-3
        themeLayout.addWidget(self.themeList,row,0,3,1)
        themeLayout.setColumnStretch(0,3)

        # Col 1, row 1
        themeLayout.addWidget(themeAddButton,row,1,1,1)
        row+=1
        # Col 1, row 2
        themeLayout.addWidget(themeRemoveButton,row,1,1,1)
        # Col 1, row 3

        themeWidget = QWidget()
        themeWidget.setLayout(themeLayout)

        prefsTab.addTab(themeWidget,"Themes")



        # Add Tab bar to mainFrame
        # --------------------------
        mainFrameLayout = QVBoxLayout()
        mainFrameLayout.addWidget(prefsTab)
        mainFrame.setLayout(mainFrameLayout)


        # Add button box to buttonFrame
        # -------------------------------
        buttonFrameLayout = QVBoxLayout()
        buttonFrameLayout.addWidget(buttonBox)
        buttonFrame.setLayout(buttonFrameLayout)


        # Layout for all the dialog
        # -------------------------
        dialogLayout = QVBoxLayout()
        dialogLayout.addWidget(mainFrame)
        dialogLayout.addWidget(buttonFrame)

        self.setLayout(dialogLayout)

        # Fill in the dialog fields
        self.populate()




    # -----------------------------------------------------------------------
    # Exiting dialog
    # -----------------------------------------------------------------------

    def exitDialog(self):
        """
        Function to execute when the OK button is clicked.
        It extracts all the paths into list variables so the caller can
        extract them.

        """

        # Get Panels paths
        # -----------------
        self.prefs.panelPaths = getPathsFromList(self.panelsList)


        # Get Scripts paths
        # -----------------
        self.prefs.scriptPaths = getPathsFromList(self.scriptsList)

        # Get transformer paths
        # -----------------
        self.prefs.transformerPaths = getPathsFromList(self.transList)

        # Get maths functions paths
        # -----------------
        self.prefs.mathFunctionPaths = getPathsFromList(self.mathsList)

        # Get Macro paths
        # -----------------
        self.prefs.macroPaths = getPathsFromList(self.macroList)

        # Get theme paths
        # -------------------
        self.prefs.theme_css = self.currentThemePath.text()
        self.prefs.themePaths =  getPathsFromList(self.themeList)


        # Exit dialog
        self.accept()

    # -----------------------------------------------------------------------
    # Populate dialog
    # -----------------------------------------------------------------------
    def populate(self):
        """
        Populate the fields of the dialog box from the Preferences class

        """

        # Paths
        # ---------
        self.setPanelPaths(self.prefs.panelPaths)
        self.setScriptPaths(self.prefs.scriptPaths)
        self.setTransformerPaths(self.prefs.transformerPaths)
        self.setMacroPaths(self.prefs.macroPaths)
        self.currentThemePath.setText(self.prefs.theme_css)




    # -----------------------------------------------------------------------
    # Panel Preferences
    # -----------------------------------------------------------------------
    def setPanelPaths(self,list_of_paths):
        """
        Set the panel paths directly

        Input
        ---------
        list_of_paths : list of str

        """

        addPathsToList(self.panelsList,list_of_paths)





    def addPanelPath(self):
        """
        Add the path in the Panel line edit to the Panel path list box.
        Checking that the path exists.

        """

        # Get path
        newPath = self.panelsPath.text()

        # Check if path exists
        if not os.path.exists(newPath):
            QMessageBox.warning(self,"Unknown path","Cannot find path [%s]" % newPath)
            return

        # add new path to list
        self.panelsList.addItem(newPath)



    def browseForPanelPath(self):
        """
        Open file dialog and get a new path

        """

        newPath = self.getPath("Select path containing panels")

        if newPath:
            self.panelsPath.setText(newPath)



    def removePanelPath(self):
        """
        Remove currently selected paths.
        Usually called by clicking 'Remove' button

        """

        selectedItems = self.panelsList.selectedItems()


        if  selectedItems == []:
            return

        for item in selectedItems:
            self.panelsList.takeItem(self.panelsList.row(item))

    # -----------------------------------------------------------------------
    # Script Preferences
    # -----------------------------------------------------------------------
    def setScriptPaths(self,list_of_paths):
        """
        Set the panel paths directly

        Input
        ---------
        list_of_paths : list of str

        """

        addPathsToList(self.scriptsList,list_of_paths)





    def addScriptPath(self):
        """
        Add the path in the Script line edit to the Script path list box.
        Checking that the path exists.

        """

        # Get path
        newPath = self.scriptsPath.text()

        # Check if path exists
        if not os.path.exists(newPath):
            QMessageBox.warning(self,"Unknown path","Cannot find path [%s]" % newPath)
            return

        # add new path to list
        self.scriptsList.addItem(newPath)



    def browseForScriptPath(self):
        """
        Open file dialog and get a new path

        """

        newPath = self.getPath("Select path containing scripts")

        if newPath:
            self.scriptsPath.setText(newPath)



    def removeScriptPath(self):
        """
        Remove currently selected paths.
        Usually called by clicking 'Remove' button

        """

        selectedItems = self.scriptsList.selectedItems()


        if  selectedItems == []:
            return

        for item in selectedItems:
            self.scriptsList.takeItem(self.scriptsList.row(item))


    # -----------------------------------------------------------------------
    # Transformer Preferences
    # -----------------------------------------------------------------------
    def setTransformerPaths(self,list_of_paths):
        """
        Set the panel paths directly

        Input
        ---------
        list_of_paths : list of str

        """

        addPathsToList(self.transList,list_of_paths)





    def addTransformerPath(self):
        """
        Add the path in the Transformer line edit to the Transformer path list box.
        Checking that the path exists.

        """

        # Get path
        newPath = self.transPath.text()

        # Check if path exists
        if not os.path.exists(newPath):
            QMessageBox.warning(self,"Unknown path","Cannot find path [%s]" % newPath)
            return

        # add new path to list
        self.transList.addItem(newPath)



    def browseForTransformerPath(self):
        """
        Open file dialog and get a new path

        """

        newPath = self.getPath("Select path containing transformers")

        if newPath:
            self.transPath.setText(newPath)



    def removeTransformerPath(self):
        """
        Remove currently selected paths.
        Usually called by clicking 'Remove' button

        """

        selectedItems = self.transList.selectedItems()


        if  selectedItems == []:
            return

        for item in selectedItems:
            self.transList.takeItem(self.transList.row(item))

    # -----------------------------------------------------------------------
    # MathFunction Preferences
    # -----------------------------------------------------------------------
    def setMathFunctionPaths(self,list_of_paths):
        """
        Set the panel paths directly

        Input
        ---------
        list_of_paths : list of str

        """

        addPathsToList(self.mathsList,list_of_paths)





    def addMathFunctionPath(self):
        """
        Add the path in the MathFunction line edit to the MathFunction path list box.
        Checking that the path exists.

        """

        # Get path
        newPath = self.mathsPath.text()

        # Check if path exists
        if not os.path.exists(newPath):
            QMessageBox.warning(self,"Unknown path","Cannot find path [%s]" % newPath)
            return

        # add new path to list
        self.mathsList.addItem(newPath)



    def browseForMathFunctionPath(self):
        """
        Open file dialog and get a new path

        """

        newPath = self.getPath("Select path containing MathFunctions")

        if newPath:
            self.mathsPath.setText(newPath)



    def removeMathFunctionPath(self):
        """
        Remove currently selected paths.
        Usually called by clicking 'Remove' button

        """

        selectedItems = self.mathsList.selectedItems()


        if  selectedItems == []:
            return

        for item in selectedItems:
            self.mathsList.takeItem(self.mathsList.row(item))


    # -----------------------------------------------------------------------
    # Macro Preferences
    # -----------------------------------------------------------------------
    def setMacroPaths(self,list_of_paths):
        """
        Set the panel paths directly

        Input
        ---------
        list_of_paths : list of str

        """

        addPathsToList(self.macroList,list_of_paths)





    def addMacroPath(self):
        """
        Add the path in the Macro line edit to the Macro path list box.
        Checking that the path exists.

        """

        # Get path
        newPath = self.macroPath.text()

        # Check if path exists
        if not os.path.exists(newPath):
            QMessageBox.warning(self,"Unknown path","Cannot find path [%s]" % newPath)
            return

        # add new path to list
        self.macroList.addItem(newPath)



    def browseForMacroPath(self):
        """
        Open file dialog and get a new path

        """

        newPath = self.getPath("Select path containing Macros")

        if newPath:
            self.macroPath.setText(newPath)



    def removeMacroPath(self):
        """
        Remove currently selected paths.
        Usually called by clicking 'Remove' button

        """

        selectedItems = self.macroList.selectedItems()


        if  selectedItems == []:
            return

        for item in selectedItems:
            self.macroList.takeItem(self.macroList.row(item))



    def browseForThemePath(self):
        """
        Open file dialog and get a new path

        """

        newFile = self.getFile("CSS files (*.css);;")

        if newFile:
            self.currentThemePath.setText(newFile)


    def addThemePath(self):
        """
        Add the path in the Theme line edit to the Theme path list box.
        Checking that the path exists.

        """

        # Get path
        newPath = self.themePath.text()

        # Check if path exists
        if not os.path.exists(newPath):
            QMessageBox.warning(self,"Unknown path","Cannot find path [%s]" % newPath)
            return

        # add new path to list
        self.themeList.addItem(newPath)


    def removeThemePath(self):
        """
        Remove currently selected paths.
        Usually called by clicking 'Remove' button

        """

        selectedItems = self.themeList.selectedItems()


        if  selectedItems == []:
            return

        for item in selectedItems:
            self.themeList.takeItem(self.themeList.row(item))



    def setDefaultThemePath(self):

        default_path = os.path.join(self.prefs.basepath,'themes/default/default.css')

        if os.path.exists(default_path):
            self.currentThemePath = default_path
        else:
            self.currentThemePath = "No path found"



    # -----------------------------------------------------------------------
    # Utilities
    # -----------------------------------------------------------------------
    def getPath(self,caption="Select folder"):
        """
        Get a path using a FileDialog, usually as a response to a "Browse..."
        button being pressed.

        Output
        --------
        newPath : str
            path returned
        """

        newPath = QFileDialog.getExistingDirectory(self,caption,self.prefs.lastPath,
                                         QFileDialog.ShowDirsOnly
                                                 | QFileDialog.DontResolveSymlinks)

        # TODO : What if user presses cancel?
        self.prefs.lastPath = newPath

        return newPath


    def getFile(self,formatString="All files (*.*);;"):


        pathAndFilename = QFileDialog.getOpenFileName(self,"Open file",
                                               self.prefs.lastPath,formatString)


        if not pathAndFilename:
            return

        return pathAndFilename







#==============================================================================
#%% Test running
#==============================================================================


if __name__ == "__main__":
    import sys

    prefs = Preferences()
    prefs.panelPaths = ['/home/john/pibble','/home/john/pobble']
    prefs.scriptPaths = ['/home/john/sibble','/home/john/sobble']
    prefs.transformerPaths = ['/home/john/tibble','/home/john/tobble']
    prefs.macroPaths = ['/home/john/mibble','/home/john/mobble']

    app = QApplication(sys.argv)
    form = PreferencesDialog(prefs=prefs)
    #form.prefs = prefs
    form.show()
    app.exec_()

    print("Panel paths:")
    print(prefs.panelPaths)

    print("Script paths:")
    print(prefs.scriptPaths)

    print("Transformer paths:")
    print(prefs.transformerPaths)

    print("Macro paths:")
    print(prefs.macroPaths)
