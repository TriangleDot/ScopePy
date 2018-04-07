"""
ScopePy: QT extra imports

Central module for importing QT.

When QT updates, this file can be changed

"""

#==============================================================================
#%% License
#==============================================================================

"""
Copyright 2016 John Bainbridge

This file is part of ScopePy.

ScopePy is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ScopePy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with ScopePy.  If not, see <http://www.gnu.org/licenses/>.
"""


try:
    from PyQt5 import QtWebKit
    from PyQt5.QtWebKit import QWebView
    import PyQt5.QtSvg as QtSvg

except:
    try:
        from PyQt4 import QtWebKit
        from PyQt4.QtWebKit import QWebView
        import PyQt4.QtSvg as QtSvg
    except:
        assert RuntimeError,"Cannot import a version of QT graphics library, tried QT5 and QT4"
