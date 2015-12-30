#!/usr/bin/env python

import gtk
import time
import os
import sys
from subprocess import Popen, PIPE
import shlex

from desktop_tool import DesktopToolWidget
from desktop_tool import get_icon as get_icon

from peppermint_sp_parse_xml import Peppermint_sp

#=======================================================================

class Config:
    # Position of NoteBook tabs gtk.POS_TOP or gtk.POS_LEFT
    TAB_POS = gtk.POS_LEFT
    # Number of columns
    NCOLUMNS = 3
    # Sizes
    ICON_SIZE = 48
    MAIN_WINDOW_BORDER_WIDTH = 5
    BTN_WIDTH = 150
    BTN_HEIGHT = 50
    # Icons
    MAIN_WINDOW_ICON = "preferences-desktop"
#=======================================================================

DEBUG = False
def debug(msg):
    if DEBUG:
        print "===> debug: " + msg

class Notebook(gtk.Notebook):

    def __init__(self):
        gtk.Notebook.__init__(self)
        self.set_tab_pos(Config.TAB_POS)

class Table(gtk.Table) :
    def __init__(self):
        gtk.Table.__init__(self)
        
    def attach(self, row, col, widget):
        # attach(child, left_attach, right_attach, top_attach, bottom_attach,..)
        gtk.Table.attach(self, widget, col, col + 1, row, row + 1)
    
class CategoryFrame(gtk.Frame) :

    def __init__(self, category):
        self.btn_height = Config.BTN_HEIGHT
        self.btn_width = Config.BTN_WIDTH
        
        gtk.Frame.__init__(self)

        self.alignment = gtk.Alignment(0.0, 0.0, 1.0, 1.0)
        self.alignment.set_padding(10, 10, 10, 10)
        self.add(self.alignment)
       
        self.table = Table()
        self.alignment.add(self.table)
        
        self.tool_button = []

        self.load_tools(category)

        
        
    def load_tools(self, category):
        
        row = 0
        col = 0
        i = 0
        for tool in category.tools:
            if Config.TAB_POS == gtk.POS_LEFT:
                orientation =  gtk.ORIENTATION_VERTICAL
                wrap_len = 20
            else:
                orientation =  gtk.ORIENTATION_HORIZONTAL
                wrap_len = 0 # no wrap
            icon_button = DesktopToolWidget(tool.label, tool.icon, Config.ICON_SIZE, orientation, wrap = wrap_len)
            self.tool_button.insert(i, icon_button)
            self.tool_button[i].set_size_request(self.btn_width, self.btn_height)
            self.tool_button[i].set_callback(self.on_item_activated, self, tool.action)

            self.table.attach(row, col, self.tool_button[i])
            self.table.set_col_spacing(col, 10)
            self.table.set_row_spacing(row, 10)
            #print "=== %s => i: %d row: %d col: %d" % (tool.label, i, row, col)
            i += 1
            col += 1
            if col == Config.NCOLUMNS:
                col = 0
                row += 1 
            
        #self.table.set_row_spacing(row, 50)
        
    def on_item_activated(self, action):
        print "on_item_activated: button [%s]" % action
        # Convert utf-8 string to ascii
        udata = action.decode("utf-8")
        asciidata = udata.encode("ascii","ignore")

        # Build the args list expected by Popen
        args = shlex.split(asciidata)
        # And start action in a subprocess
        print args
        process = Popen(args, stdout=PIPE, stderr=PIPE)


class MainWindow:
    
    def __init__(self):
        window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        window.set_position(gtk.WIN_POS_CENTER)
        window.set_border_width(Config.MAIN_WINDOW_BORDER_WIDTH)
        pixbuf = get_icon(Config.MAIN_WINDOW_ICON, 16)
        window.set_icon(pixbuf)
        window.connect("delete_event", self.onDeleteEvent)

        # Create a new notebook
        self.notebook = Notebook()

        # Add the tab pages
        cat_index = 0
        
        peppermint_sp = Peppermint_sp("peppermint_sp.xml")
        #print peppermint_sp.to_string()

        window.set_title(peppermint_sp.title)

        for category in peppermint_sp.categories:
            
            category_name = category.title
            
            if True:
                tab_box = gtk.HBox(False, 2)
                tab_box.set_spacing(8)
                tab_label = gtk.Label(category_name)
                cat_index += 1

                pixbuf = get_icon(category.icon, Config.ICON_SIZE)
                tab_icon = gtk.Image()
                tab_icon.set_from_pixbuf(pixbuf)
                
                tab_icon.set_size_request(-1, 60)
                tab_box.pack_start(tab_icon, False)
                tab_box.pack_start(tab_label, False)

                # needed, otherwise even calling show_all on the notebook won't
                # make the hbox contents appear.
                tab_box.show_all()

            else:
                # tentative: ne convient pas: l'onglet a un ombrage de style bouton...
                tab_box = DesktopToolWidget(category_name, category.icon, Config.ICON_SIZE, gtk.ORIENTATION_HORIZONTAL)
            
            for tool in category.tools:
                frame = CategoryFrame(category)
                #assert frame.get_parent()
                #assert tab_box.get_parent()
                frame.show_all()
            
            self.notebook.append_page(frame, tab_box)
        
        # Set what page to start at
        self.notebook.set_current_page(0)
        self.notebook.show_all()
        window.add(self.notebook)
        
        window.show_all()

    def onDeleteEvent(self, widget, event=None, *arguments, **keywords):
        gtk.main_quit()
        return False


def main():
  gtk.main()
  return 0


if __name__ == "__main__":
    try:
        MainWindow()
        main()
    except KeyboardInterrupt:
        print "\nBye."
        sys.exit()
