#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.MenuList import MenuList
from Components.MultiContent import MultiContentEntryText
from Components.MultiContent import MultiContentEntryPixmapAlphaTest
from Components.Pixmap import Pixmap, MovingPixmap
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor
from Components.PluginComponent import plugins
from Components.PluginList import PluginEntryComponent
from Components.ConfigList import ConfigListScreen
from Components.config import config, getConfigListEntry
from Components.config import ConfigEnableDisable, ConfigSubsection
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from enigma import eListboxPythonMultiContent, gFont
from enigma import RT_HALIGN_LEFT, RT_VALIGN_CENTER
from enigma import loadPNG
import os
import re
import shutil
from enigma import getDesktop


# this is old plugin i have adapted
# and update to 2023-06-07  @Lululla @linux-sat forum
# work on atv 7.2/4(dev) - BH Image HD & FHD
# PY2/PY3 compatible

version = 'v.1.1'
config.plugins.PluginsPanel = ConfigSubsection()
config.plugins.PluginsPanel.hits = ConfigEnableDisable(default=False)


def getDesktopSize():
    s = getDesktop(0).size()
    return (s.width(), s.height())


def isUHD():  # to future
    desktopSize = getDesktopSize()
    return desktopSize[0] == 3840


def isFHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] == 1920


def isHD():
    desktopSize = getDesktopSize()
    return desktopSize[0] >= 1280 and desktopSize[0] < 1920


class mylist(MenuList):

    def __init__(self, list):

        MenuList.__init__(self, list, True, eListboxPythonMultiContent)
        if isFHD():
            self.l.setItemHeight(50)
            textfont = int(30)
            self.l.setFont(0, gFont('Regular', textfont))
        else:
            self.l.setItemHeight(50)
            textfont = int(24)
            self.l.setFont(0, gFont('Regular', textfont))


class PluginsPanel(Screen):

    def __init__(self, session, plugin_path):

        self.plugin_path = plugin_path
        self.skin_path = plugin_path
        self.session = session
        self.pluginlist = plugins.getPlugins(PluginDescriptor.WHERE_PLUGINMENU)
        self.list = [PluginEntryComponent(plugin) for plugin in self.pluginlist]
        self.list_new = []

        config_rds = open(self.plugin_path + '/config', 'w')

        for plugin_data in self.list:
            plugin_start, plugin_name, plugin_desc, plugin_icon = plugin_data
            self.list_new.append((plugin_start,
                                  plugin_name[7],
                                  plugin_desc[7],
                                  plugin_icon[5],
                                  '0',
                                  '0'))
            config_rds.write('"%s" "%s" "%s"\n' % (plugin_name[7], '0', '0'))
        config_rds.close()
        self.list = self.list_new

        if config.plugins.PluginsPanel.hits.value:
            self.list.sort(key=lambda x: int(x[4]))
            self.list.reverse()
        print('[wall-e]: Plugin count:', len(self.list))

        self.posi = []
        skincontent = ''

        if isFHD():
            posx = 10
            posy = 70
            for x in range(len(self.list)):
                if x == 6 or x == 12 or x == 18 or x == 24 or x == 30:
                    posx = 10
                    posy += 100
                self.posi.append((posx, posy))
                skincontent += '<widget name="zeile' + str(x) + '" position="' + str(posx) + ',' + str(posy) + '" size="180,85" scale="stretch" alphatest="blend" />'
                posx += 200
            self.skin = '<screen name="PluginsPanel" position="360,220" size="1200,767" title=""><widget name="frame" position="10,80" size="184,89" pixmap="~/images/framefhd.png" zPosition="5" alphatest="on" /><widget name="info" position="0,2" size="1195,59" valign="center" halign="center" zPosition="10" font="Regular;32" foregroundColor="#007fcfff" transparent="1" /><widget name="disc" position="3,670" size="1200,47" valign="center" halign="center" zPosition="10" font="Regular;28" foregroundColor="yellow" transparent="1" /><ePixmap position="6,725" size="20,20" pixmap="~/images/green.png" zPosition="5" alphatest="blend" /><widget name="key_green" position="35,715" size="364,40" valign="center" halign="left" zPosition="10" font="Regular;24" foregroundColor="yellow" transparent="1" />' + skincontent + '</screen>'

        else:  # isHD()
            posx = 10
            posy = 30
            for x in range(len(self.list)):
                if x == 5 or x == 10 or x == 15 or x == 20 or x == 25:
                    posx = 10
                    posy += 60
                self.posi.append((posx, posy))
                skincontent += '<widget name="zeile' + str(x) + '" position="' + str(posx) + ',' + str(posy) + '" size="100,40" alphatest="blend" />'
                posx += 120
            self.skin = '<screen name="PluginsPanel" position="center,center" size="610,455" title=""><widget name="frame" position="10,10" size="107,50" pixmap="~/images/frame.png" zPosition="5" alphatest="on" /><widget name="info" position="0,2" size="610,24" valign="center" halign="center" zPosition="10" font="Regular;24" foregroundColor="#007fcfff" transparent="1" /><widget name="disc" position="0,378" size="610,20" valign="center" halign="center" zPosition="10" font="Regular;19" foregroundColor="yellow" transparent="1" />' + skincontent + '<ePixmap pixmap="~/images/green.png" position="10,410" size="20,20" zPosition="5" alphatest="blend" /><widget name="key_green" position="35,402" size="364,40" valign="center" halign="left" zPosition="10" font="Regular;20" foregroundColor="yellow" transparent="1" /></screen>'

        Screen.__init__(self, session)
        self['actions'] = ActionMap(['OkCancelActions',
                                     'ColorActions',
                                     'DirectionActions'], {'cancel': self.exit,
                                                                'ok': self.ok,
                                                                'green': self.wall_sort,
                                                                'blue': self.wall_config,
                                                                'left': self.left,
                                                                'right': self.right,
                                                                'up': self.up,
                                                                'down': self.down}, -1)
        self['frame'] = MovingPixmap()
        self['info'] = Label('')
        self['disc'] = Label('')
        self['key_green'] = Label('Sort')
        for x in range(len(self.list)):
            self.at = 29
            if isFHD():
                self.at = 34
            if x <= int(self.at):
                self['zeile' + str(x)] = Pixmap()
                self['zeile' + str(x)].show()
            else:
                self['zeile' + str(x)] = Pixmap()
                self['zeile' + str(x)].hide()

        self.achsex = 0
        if config.plugins.PluginsPanel.hits.value:
            print('YEEES')
        self.onFirstExecBegin.append(self._onFirstExecBegin)

    def wall_sort(self):
        self.list.sort(key=lambda x: int(x[4]))
        self.list.reverse()
        self._onFirstExecBegin()

    def wall_config(self):
        self.session.openWithCallback(self.closen, PluginsPanel_config, plugin_path)

    def closen(self, data):
        print('data: ', data)
        print(config.plugins.PluginsPanel.hits.value)
        self.close(self.session, 'main')

    def paintnew(self, a, b):
        print('[wall-e]: Moving to:', a, b)
        self['info'].setText('%s' % self.list[self.achsex][1])
        self['disc'].setText('%s' % self.list[self.achsex][2])
        self['frame'].moveTo(int(a) - 3, int(b) - 3, 1)
        self['frame'].startMoving()
        self['frame'].show()

    def left(self):
        print('[wall-e]: Position:', self.achsex)
        if not self.achsex <= 0:
            self.achsex -= 1
        print('[wall-e]: Position:', self.achsex)
        self.paintnew(self.posi[self.achsex][0], self.posi[self.achsex][1])

    def right(self):
        print('[wall-e]: Position:', self.achsex)
        if not self.achsex == int(self.at):
            if not self.achsex == len(self.list) - 1:
                self.achsex += 1
            else:
                self.achsex = 0
        print('[wall-e]: Position:', self.achsex)
        self.paintnew(self.posi[self.achsex][0], self.posi[self.achsex][1])

    def up(self):
        print('[wall-e]: Position:', self.achsex)
        self.bt = 4
        if isFHD():
            self.bt = 6
        if not self.achsex <= int(self.bt):
            if isFHD():
                self.achsex -= 6
            else:
                self.achsex -= 5
        if self.achsex <= int(self.bt):
            self.achsex = len(self.list) - 1
        print('[wall-e]: Position:', self.achsex)
        self.paintnew(self.posi[self.achsex][0], self.posi[self.achsex][1])

    def down(self):
        print('[wall-e]: Position:', self.achsex)
        self.bt = 24
        if isFHD():
            self.bt = 29
        if not self.achsex > int(self.bt):
            self.ct = 5
            if isFHD():
                self.ct = 6

            if not self.achsex >= len(self.list) - int(self.ct):
                self.achsex += int(self.ct)
            else:
                self.achsex = 0
        else:
            self.achsex = 0
        print('[wall-e]: Position:', self.achsex)
        self.paintnew(self.posi[self.achsex][0], self.posi[self.achsex][1])

    def _onFirstExecBegin(self):
        for x in range(len(self.list)):
            self['zeile' + str(x)].instance.setPixmap(self.list[x][3])
            self['zeile' + str(x)].show()
        self.setTitle('Plugins Panel %s - Shows %s Plugins' % (version, len(self.list)))
        self.paintnew(self.posi[self.achsex][0], self.posi[self.achsex][1])

    def ok(self):
        plugin = self.list[self.achsex][0]
        plugin(session=self.session)

    def exit(self):
        self.close(self.session, '')


class PluginsPanel_config(Screen, ConfigListScreen):

    skin = """
            <screen position="center,center" size="633,484" title="Wall Setup">
                <widget name="config" position="20,20" size="595,50" scrollbarMode="showNever" itemHeight="50" />
                <widget name="config2" position="20,100" size="595,320" scrollbarMode="showOnDemand" />
                <!--
                <ePixmap position="30,440" size="20,20" pixmap="~/images/green.png" zPosition="5" alphatest="blend" />
                <widget name="key_green" position="60,430" size="364,40" valign="center" halign="left" zPosition="10" font="Regular;19" foregroundColor="yellow" transparent="1" />
                --->
            </screen>"""

    def __init__(self, session, plugin_path):

        Screen.__init__(self, session)
        self.plugin_path = plugin_path
        self.skin_path = plugin_path
        self.session = session
        # self.list = []
        self.onChangedEntry = []
        self['config2'] = mylist([])
        # ConfigListScreen.__init__(self, self.list)
        # self.list.append(getConfigListEntry('Sort by plugin hits:', config.plugins.PluginsPanel.hits))
        # self['config'].setList(self.list)
        # self['config'].setItemHeight(50)
        # self['key_green'] = Label('Sort')
        self['setupActions'] = ActionMap(['SetupActions', 'ColorActions'], {
                                          'ok': self.change_hide,
                                          # 'green': self.changeHits,
                                          'cancel': self.saveConfig}, -1)
        self.readconfig()

    # def changedEntry(self):
        # for x in self.onChangedEntry:
            # x()

    # def getCurrentEntry(self):
        # return self["config"].getCurrent()[0]

    # def getCurrentValue(self):
        # return str(self["config"].getCurrent()[1].getText())

    # def createSummary(self):
        # from Screens.Setup import SetupSummary
        # return SetupSummary

    # def changeHits(self):
        # if config.plugins.PluginsPanel.hits.value == False:
            # config.plugins.PluginsPanel.hits.setValue(True)
        # else:
            # config.plugins.PluginsPanel.hits.setValue(False)

        # config.plugins.PluginsPanel.hits.save()
        # self.readconfig()

    def readconfig(self):
        # list = self.list
        # del list[:]

        config_read = open(self.plugin_path + '/config', 'r')
        self.config_list = []
        for line in config_read.readlines():
            ok = re.findall('"(.*?)" "(.*?)" "(.*?)"', line, re.S)
            if ok:
                name, hits, hide = ok[0]
                self.config_list.append(self.show_menu(name, hits, hide))

        config_read.close()
        self['config2'].l.setList(self.config_list)
        # self.list.append(getConfigListEntry('Sort by plugin hits:', config.plugins.PluginsPanel.hits.value))
        # self["config"].list = self.list
        # self["config"].l.setList(self.list)

    def show_menu(self, name, hits, hide):
        res = [(name, hits, hide)]
        if isFHD():
            if int(hide) == 0:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(15, 14), size=(20, 20), png=loadPNG(self.plugin_path + '/images/greens.png')))
            else:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(15, 14), size=(20, 20), png=loadPNG(self.plugin_path + '/images/reds.png')))
            res.append(MultiContentEntryText(pos=(50, 0), size=(450, 50), font=0, text=name, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
        else:
            if int(hide) == 0:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(15, 12), size=(20, 20), png=loadPNG(self.plugin_path + '/images/greens.png')))
            else:
                res.append(MultiContentEntryPixmapAlphaTest(pos=(15, 12), size=(20, 20), png=loadPNG(self.plugin_path + '/images/reds.png')))
            res.append(MultiContentEntryText(pos=(50, 0), size=(450, 45), font=0, text=name, flags=RT_HALIGN_LEFT | RT_VALIGN_CENTER))
        return res

    def change_hide(self):
        print('ok')
        item = self['config2'].getCurrent()
        if item:
            list_name = item[0][0]
            print(list_name)
            config_read = open(self.plugin_path + '/config', 'r')
            config_tmp = open(self.plugin_path + '/config_tmp', 'w')
            for line in config_read.readlines():
                ok = re.findall('"(.*?)" "(.*?)" "(.*?)"', line, re.S)
                if ok:
                    name, hits, hide = ok[0]
                    if list_name.lower() == name.lower():
                        if int(hide) == 0:
                            config_tmp.write('"%s" "%s" "%s"\n' % (name, hits, '1'))
                        else:
                            config_tmp.write('"%s" "%s" "%s"\n' % (name, hits, '0'))
                    else:
                        config_tmp.write('"%s" "%s" "%s"\n' % (name, hits, hide))
            config_tmp.close()
            config_read.close()
            shutil.move(self.plugin_path + '/config_tmp', self.plugin_path + '/config')
            self.readconfig()

    def saveConfig(self):
        print('save')
        # for x in self['config'].list:
            # x[1].save()

        self.close('True')

    def exit(self):
        print('closen')
        self.close('False')


def main(session, **kwargs):
    session.openWithCallback(closen, PluginsPanel, plugin_path)


def closen(session, result):
    if result == 'main':
        session.openWithCallback(closen, PluginsPanel, plugin_path)


def menu(menuid, **kwargs):
    if menuid == 'mainmenu':
        return [(_('Plugins Panel'),
                 main,
                 'pluginspanel_mainmenu',
                 44)]
    return []


def Plugins(path, **kwargs):
    global plugin_path
    plugin_path = path
    icon = 'plugin.png'
    # if isFHD():
        # icon = 'pluginHD.png'
    list = []
    list.append(PluginDescriptor(icon='plugin.png', name='PluginsPanel', description='This Panel Show Plugins', where=PluginDescriptor.WHERE_MENU, fnc=menu))
    list.append(PluginDescriptor(icon='plugin.png', name='PluginsPanel', description='This Panel Show Plugins', where=PluginDescriptor.WHERE_PLUGINMENU, fnc=main))
    return list
