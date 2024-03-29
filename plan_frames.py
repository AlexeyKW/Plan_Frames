# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PlanFrames
                                 A QGIS plugin
 Создание рамок для планов масштабов 1:500 1:1000 1:2000 1:5000
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2019-11-13
        git sha              : $Format:%H$
        copyright            : (C) 2019 by Alexey Kolesnikov
        email                : a.a.kolesnikov@sgugit.ru
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .plan_frames_dialog import PlanFramesDialog
import os.path

from qgis.core import (
    Qgis,
    QgsFieldProxyModel,
    QgsMapLayer,
    QgsMapLayerProxyModel,
    QgsMessageLog,
    QgsProject,
    QgsVectorLayer,
    QgsWkbTypes,
    QgsFeature,
    QgsGeometry,
    edit,
    QgsPointXY
)

class PlanFrames:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'PlanFrames_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&PlanFrames')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('PlanFrames', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/plan_frames/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Рамки для планов'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&PlanFrames'),
                action)
            self.iface.removeToolBarIcon(action)

    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = PlanFramesDialog()

        # show the dialog
        self.dlg.pushButton.clicked.connect(self.makeFrame)
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            #names = [layer.name() for layer in QgsProject.instance().mapLayers().values()]
            #QgsMessageLog.logMessage(frame_layer.name())
            #frame_layer.updateExtents()
            #QgsMessageLog.logMessage(self.dlg.lineEdit.text())
            pass
        self.dlg.pushButton.disconnect()

    def makeFrame(self):
        #QgsMessageLog.logMessage("test1")
        #QgsMessageLog.logMessage(self.dlg.comboBox.currentText())
        if self.dlg.comboBox.currentText() == '1:500':
            delta=250
            section = 5
        if self.dlg.comboBox.currentText() == '1:1000':
            delta=500
            section = 5
        if self.dlg.comboBox.currentText() == '1:2000':
            delta=1000
            section = 5
        if self.dlg.comboBox.currentText() == '1:5000':
            delta=2000
            section = 5
        if self.dlg.comboBox.currentText() == '1:5000 размер планшета 2500м':
            delta=2500
            section = 5
        if self.dlg.comboBox.currentText() == '1:5000 планшет 40x40см, размер планшета 2000м':
            delta=2000
            section = 4
        X1=self.dlg.lineEdit.text()
        Y1=self.dlg.lineEdit_2.text()
        X2=X1
        Y2=str(int(Y1)+delta)
        X3=str(int(X2)+delta)
        Y3=Y2
        X4=X3
        Y4=Y1
        X5=X1
        Y5=Y1
        wkt_coords = ''
        wkt_coords = X1+' '+Y1+', '+X2+' '+Y2+', '+X3+' '+Y3+', '+X4+' '+Y4+', '+X5+' '+Y5
        frame_layer = QgsProject.instance().mapLayersByName("frames")[0]
        grid_layer = QgsProject.instance().mapLayersByName("grids")[0]
        fields = frame_layer.fields()
        fields_grid = grid_layer.fields()
        frame_feature = None
        frame_feature = QgsFeature()
        frame_feature.setFields(fields)
        frame_feature['secrecy'] = self.dlg.comboBox_2.currentText()
        frame_feature['scale'] = self.dlg.comboBox.currentText()
        frame_feature['year'] = self.dlg.lineEdit_3.text()
        frame_feature['filename'] = self.dlg.lineEdit_4.text()
        #frame_feature.setGeometry(QgsGeometry.fromWkt('polygon((100 200, 200 300, 200 400, 120 180, 100 200))'))
        frame_feature.setGeometry(QgsGeometry.fromWkt('polygon(('+wkt_coords+'))'))
        frame_layer.startEditing()
        frame_layer.dataProvider().addFeatures([frame_feature])
        #QgsMessageLog.logMessage(str(wkt_coords))
        if self.dlg.checkBox.isChecked():
            grid_layer.startEditing()
            for i in range(1,section):
                grid_wkt_v=''
                grid_wkt_v = 'linestring('+str(int(X1)+delta/section*i)+' '+Y1+', '+str(int(X1)+delta/section*i)+' '+Y2+')'
                grid_feature = None
                grid_feature = QgsFeature()
                grid_feature.setGeometry(QgsGeometry.fromWkt(grid_wkt_v))
                grid_feature.setFields(fields_grid)
                grid_feature['filename'] = self.dlg.lineEdit_4.text()
                grid_layer.dataProvider().addFeatures([grid_feature])
                grid_wkt_h=''
                grid_wkt_h = 'linestring('+X1+' '+str(int(Y1)+delta/section*i)+', '+X3+' '+str(int(Y1)+delta/section*i)+')'
                grid_feature = None
                grid_feature = QgsFeature()
                grid_feature.setGeometry(QgsGeometry.fromWkt(grid_wkt_h))
                grid_feature.setFields(fields_grid)
                grid_feature['filename'] = self.dlg.lineEdit_4.text()
                grid_layer.dataProvider().addFeatures([grid_feature])
            grid_layer.updateExtents()
            grid_layer.commitChanges()
        frame_layer.updateExtents() 
        frame_layer.commitChanges()