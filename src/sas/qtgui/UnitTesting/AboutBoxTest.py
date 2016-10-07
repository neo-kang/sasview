import sys
import unittest
import webbrowser

from PyQt4.QtGui import *
from PyQt4.QtTest import QTest
from PyQt4.QtCore import *
from mock import MagicMock

# Local
from AboutBox import AboutBox
import LocalConfig

app = QApplication(sys.argv)

class AboutBoxTest(unittest.TestCase):
    '''Test the AboutBox'''
    def setUp(self):
        '''Create the AboutBox'''
        self.widget = AboutBox(None)

    def tearDown(self):
        '''Destroy the AboutBox'''
        self.widget.close()
        self.widget = None

    def testDefaults(self):
        '''Test the GUI in its default state'''
        self.assertIsInstance(self.widget, QWidget)
        self.assertEqual(self.widget.windowTitle(), "About")
        self.assertEqual(self.widget.cmdOK.text(), "OK")

        self.assertIn("SasView", self.widget.label_2.text())
        # Link buttons pixmaps don't contain image filenames, so can't check this.
        # self.assertEqual(self.widget.cmdLinkUT.icon().name(), "utlogo.gif")


    def testVersion(self):
        """
        Assure the version number is as expected
        """
        version = self.widget.lblVersion
        self.assertIsInstance(version, QLabel)
        self.assertEqual(str(version.text()), str(LocalConfig.__version__))

    def testAbout(self):
        """
        Assure the about label is filled properly
        """
        about = self.widget.lblAbout
        self.assertIsInstance(about, QLabel)
        # build version
        self.assertIn(str(LocalConfig.__build__), about.text())
        # License
        self.assertIn(str(LocalConfig._copyright), about.text())
        # URLs
        self.assertIn(str(LocalConfig._homepage), about.text())
        self.assertIn(str(LocalConfig.__download_page__), about.text())
        self.assertIn(str(LocalConfig._license), about.text())

        # Are links enabled?
        self.assertTrue(about.openExternalLinks())

    def testAddActions(self):
        """
        Assure link buttons are set up correctly
        """
        webbrowser.open = MagicMock()
        all_hosts = [
                LocalConfig._nist_url,
                LocalConfig._umd_url,
                LocalConfig._sns_url,
                LocalConfig._nsf_url,
                LocalConfig._isis_url,
                LocalConfig._ess_url,
                LocalConfig._ill_url,
                LocalConfig._ansto_url,
                LocalConfig._inst_url]

        # Press the buttons
        buttonList = self.widget.findChildren(QPushButton)
        for button in buttonList:
            QTest.mouseClick(button, Qt.LeftButton)
            #open_link = webbrowser.open.call_args
            args, _ = webbrowser.open.call_args
            # args[0] contains the actual argument sent to open()
            self.assertIn(args[0], all_hosts)

        # The above test also greedily catches the OK button,
        # so let's test it separately.
        # Show the widget
        self.widget.show()
        self.assertTrue(self.widget.isVisible())
        # Click on the OK button
        QTest.mouseClick(self.widget.cmdOK, Qt.LeftButton)
        # assure the widget is no longer seen
        self.assertFalse(self.widget.isVisible())

if __name__ == "__main__":
    unittest.main()
