#!/usr/bin/python
# requires sudo apt-get install python-gi
import os
import sys
import subprocess
import uuid
import socket
import httplib
import gi
from gi.repository import Gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify
from os.path import basename

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')


#########################################################


def generate_random_string(string_length=11):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())   # Convert UUID format to a Python string.
    # random = random.upper()   # Make all characters uppercase.
    random = random.replace("-", "")   # Remove the UUID '-'.
    return random[0:string_length]   # Return the random string.
#########################################################


def UpdateGUI():
    while Gtk.events_pending:
        Gtk.main_iteration_do(False)
#########################################################


def notif_msg(app, msg):
    # icon = APPDIR+"/notebox.png"
    # os.system("notify-send -i "+icon+" Notebox \""+msg+"\"")
    n = Notify.Notification.new(app, msg, "")
    n.show()


#########################################################


def set_winsize(win):
    # Replace w with the GtkWindow of your application
    # w = Gtk.Window()
    # Get the screen from the GtkWindow
    s = win.get_screen()
    # Using the screen of the Window, the monitor it's on can be identified
    m = s.get_monitor_at_window(s.get_active_window())
    # Then get the geometry of that monitor
    monitor = s.get_monitor_geometry(m)
    # This is an example output
    print("Monitor Heigh: %s, Width: %s" % (monitor.height, monitor.width))
    #  =========

    win.set_default_size(monitor.width-monitor.width/3, monitor.height-monitor.height/3)
    win.set_border_width(2)
    win.set_position(1)

# #######################################For sorting the list


def getKey(item):
    return item[2]
################################################################


HomeDir = os.environ['HOME']
NOTEBOXCONF = HomeDir+"/.notebox/notebox.conf"
BASEDIR = HomeDir+"/.notebox/notes"
APP = "Notebox"
APPDIR = HomeDir+"/.notebox"
G_NOTESDAT = BASEDIR+"/notebox.dat"
LCKFILE = HomeDir+"/.notebox/notebox.lck"
filename = ""
group = ""

#######################
# Read config file
G_EVERNOTEFLAG = "0"
G_EVERNOTENOTEBLIST = ""
G_DROPBOXFLAG = "0"
G_DROPBOXDIR = ""
G_MYNOTESGEARFLAG = "0"
G_MYNOTESGEARDIR = ""
G_REMINDERDIR = ""
G_REMINDERFLAG = "0"
G_MINUTESFLAG = "0"
G_MINUTESDIR = ""
G_ENCFSFLAG = "0"
G_ENCFSDIR = ""
try:
    G_EVERNOTEFLAG = subprocess.check_output("grep -c EVERNOTE=1 "+NOTEBOXCONF, shell=True)
except:
    G_EVERNOTEFLAG = "0"
G_EVERNOTEFLAG = G_EVERNOTEFLAG.rstrip('\n')

try:
    G_EVERNOTENOTEBLIST = subprocess.check_output("grep EVERNOTENOTEBLIST "+NOTEBOXCONF+" | cut -d= -f 2", shell=True)
except:
    G_EVERNOTENOTEBLIST = ""

G_EVERNOTENOTEBLIST = G_EVERNOTENOTEBLIST.rstrip('\n')

try:
    G_DROPBOXFLAG = subprocess.check_output("grep -c DROPBOX=1 "+NOTEBOXCONF, shell=True)
except:
    G_DROPBOXFLAG = "0"

G_DROPBOXFLAG = G_DROPBOXFLAG.rstrip('\n')


if G_DROPBOXFLAG == "1":
    try:
        G_DROPBOXDIR = subprocess.check_output("grep DROPBOXDIR "+NOTEBOXCONF+" | cut -d= -f 2", shell=True)
    except:
        dummy = None

    G_DROPBOXDIR = G_DROPBOXDIR.rstrip('\n')
    if not os.path.isdir(G_DROPBOXDIR):
        print "Cannot access Dropbox directory. Ignoring"
        G_DROPBOXFLAG = "0"

try:
    G_MINUTESFLAG = subprocess.check_output("grep -c MINUTES=1 "+NOTEBOXCONF, shell=True)
    G_MINUTESFLAG = G_MINUTESFLAG.rstrip('\n')
    G_MINUTESDIR = subprocess.check_output("grep MINUTESDIR "+NOTEBOXCONF+"|cut -d= -f 2 ", shell=True)
    G_MINUTESDIR = G_MINUTESDIR.rstrip('\n')
except:
    G_MINUTESFLAG = "0"

try:
    G_MYNOTESGEARFLAG = subprocess.check_output("grep -c MYNOTESGEAR=1 "+NOTEBOXCONF, shell=True)
    G_MYNOTESGEARFLAG = G_MYNOTESGEARFLAG.rstrip('\n')
    G_MYNOTESGEARDIR = subprocess.check_output("grep MYNOTESGEARDIR "+NOTEBOXCONF+"|cut -d= -f 2 ", shell=True)
    G_MYNOTESGEARDIR = G_MYNOTESGEARDIR.rstrip('\n')
except:
    G_MYNOTESGEARFLAG = "0"

try:
    G_REMINDERFLAG = subprocess.check_output("grep -c REMINDER=1 "+NOTEBOXCONF, shell=True)
    G_REMINDERFLAG = G_REMINDERFLAG.rstrip('\n')
    G_REMINDERDIR = subprocess.check_output("grep REMINDERDIR "+NOTEBOXCONF+"|cut -d= -f 2 ", shell=True)
    G_REMINDERDIR = G_REMINDERDIR.rstrip('\n')
except:
    G_REMINDERFLAG = "0"


try:
    G_ENCFSFLAG = subprocess.check_output("grep -c ENCFS=1 "+NOTEBOXCONF, shell=True)
    G_ENCFSFLAG = G_ENCFSFLAG.rstrip('\n')
    G_ENCFSDIR = subprocess.check_output("grep ENCFSDIR "+NOTEBOXCONF+"|cut -d= -f 2 ", shell=True)
    G_ENCFSDIR = G_ENCFSDIR.rstrip('\n')
except:
        G_ENCFSDIR = ""
        G_ENCFSFLAG = "0"

#######################


class notes():
    def __init__(self, title, group, notefile, tstamp, header):
        self.title = title
        self.group = group
        self.notefile = notefile
        self.notestamp = tstamp
        self.header = header

class MyWindow(Gtk.Window):

    def __init__(self):
        self.grplist = []
        self.notelist = []
        self.sortnotelist = []

        # Settings entry boxes
        self.entrydrp = None
        self.buttondrp = None
        self.drpfolder = ""
        self.minfolder = ""
        self.mynfolder = ""
        self.labelevernnblist = None

        Gtk.Window.__init__(self, title="Notebox")
        self.set_icon_from_file(APPDIR+"/notes.png")

        # self.set_default_size(monitor.width-monitor.width/3, monitor.height-monitor.height/3)
        # self.set_border_width(2)
        # self.set_position(1)

        set_winsize(self)

        self.connect("delete-event", self.delete_event)

        vboxnote = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        vboxnote.show()

        ##########################
        frame = Gtk.Frame()

        toolbar = Gtk.Toolbar()
        frame.add(toolbar)
        toolbar.show()
        frame.show()
        vboxnote.pack_start(frame, False, False, 0)

        tb_btn_addnote = Gtk.ToolButton(stock_id=Gtk.STOCK_NEW)
        tb_btn_addnote.connect("clicked", self.on_addbutton_clicked)
        tb_btn_addnote.set_tooltip_text("Create Note")
        # tb_btn_addnote.set_icon_widget(APPDIR+"/plusgrp.png")
        toolbar.add(tb_btn_addnote)

        tb_btn_delnote = Gtk.ToolButton(stock_id=Gtk.STOCK_DELETE)
        tb_btn_delnote.connect("clicked", self.on_delbutton_clicked)
        tb_btn_delnote.set_tooltip_text("Delete Note")
        image = Gtk.Image()
        image.set_from_file(APPDIR+"/trashcan.png")
        tb_btn_delnote.set_icon_widget(image)
        toolbar.add(tb_btn_delnote)

        tb_btn_reload = Gtk.ToolButton(stock_id=Gtk.STOCK_REFRESH)
        tb_btn_reload.connect("clicked", self.on_reloadbutton_clicked)
        tb_btn_reload.set_tooltip_text("Reload Notes")
        # tb_btn_reload.set_icon_from_file(APPDIR+"/plusgrp.png")
        toolbar.add(tb_btn_reload)

        tb_btn_settings = Gtk.ToolButton(stock_id=Gtk.STOCK_PREFERENCES)
        tb_btn_settings.connect("clicked", self.on_settingsbutton_clicked)
        tb_btn_settings.set_tooltip_text("Settings")
        # tb_btn_reload.set_icon_from_file(APPDIR+"/plusgrp.png")
        toolbar.add(tb_btn_settings)

        tb_btn_findnote = Gtk.ToolItem()
        self.find_entry = Gtk.Entry()
        self.find_entry.set_icon_from_icon_name(1, "edit-find")
        # self.find_entry.set_icon_from_icon_name(1,"list-add")
        tb_btn_findnote.add(self.find_entry)
        # tb_btn_findnote.connect("clicked", self.on_findbutton_clicked)
        self.find_entry.connect("activate", self.on_findbutton_activated)
        tb_btn_findnote.set_tooltip_text("Find Note")
        toolbar.add(tb_btn_findnote)

        # List
        hpaned = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        hpaned.set_position(150)

        vboxnote.pack_start(hpaned, True, True, 0)

        hpaned.show()

        scrollleft = Gtk.ScrolledWindow()
        scrollleft.show()
        scrollleft.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)


        ###########################
        #                              grpname, icon name,type
        # self.LStr_grps = Gtk.ListStore(str,str,str)

        self.rmenu = Gtk.Menu()
        self.delitem = Gtk.MenuItem("Delete...")
        self.renitem = Gtk.MenuItem("Rename...")
        self.rmenu.append(self.delitem)
        self.rmenu.append(self.renitem)
        self.delitem.connect("activate", self.on_menudel)
        self.renitem.connect("activate", self.on_menuren)
        self.delitem.show()
        self.renitem.show()

        self.LStr_grps = self.__db_loadnotegroups()

        if len(self.LStr_grps) == 1:
            self.__db_addnotegroup()

        self.treeviewgrps = Gtk.TreeView(model=self.LStr_grps)
        self.treeviewgrps.set_rules_hint(True)

        treeviewgrpcolumn = Gtk.TreeViewColumn("Note Groups")
        self.treeviewgrps.append_column(treeviewgrpcolumn)
        self.treeviewgrps.connect("row-activated", self.on_treeviewgrp_activated)
        self.treeviewgrps.connect("button_press_event", self.on_treeviegrp_event)
        cellrenderertextgrp = Gtk.CellRendererText()
        treeviewgrpcolumn.pack_start(cellrenderertextgrp, True)
        treeviewgrpcolumn.add_attribute(cellrenderertextgrp, "text", 0)
        # self.treeviewgrps.set_grid_lines(1)
        self.treeviewgrps.set_activate_on_single_click(True)
        self.treeviewgrps.set_headers_visible(False)

        cellrendererpixbuf = Gtk.CellRendererPixbuf()
        treeviewcolumn = Gtk.TreeViewColumn("", cellrendererpixbuf, icon_name=1)
        self.treeviewgrps.append_column(treeviewcolumn)
        # treeviewcolumn.pack_start(cellrendererpixbuf, False)
        # treeviewcolumn.add_attribute(cellrendererpixbuf, "pixbuf", 1)

       # ########################
        scrollleft.add(self.treeviewgrps)

        hpaned.add1(scrollleft)

        scrollright = Gtk.ScrolledWindow()
        scrollright.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        #                               title+header,title,group,filepath o evernote
        self.LStr_notes = Gtk.ListStore(str, str, str, str)
        self.__db_reloadnotes()

        self.treeviewnotes = Gtk.TreeView(model=self.LStr_notes)
        self.treeviewnotes.set_rules_hint(True)
        treeviewnotecolumn = Gtk.TreeViewColumn("Notes")
        self.treeviewnotes.append_column(treeviewnotecolumn)
        self.treeviewnotes.connect("row-activated", self.on_treeviewnote_activated)
        cellrenderertextnote = Gtk.CellRendererText()
        treeviewnotecolumn.pack_start(cellrenderertextnote, True)
        treeviewnotecolumn.add_attribute(cellrenderertextnote, "text", 0)
        self.treeviewnotes.set_grid_lines(1)

        # hboxlists.pack_start(self.treeview, True, True, 0)
        scrollright.add(self.treeviewnotes)
        hpaned.add2(scrollright)

        #########################

        self.add(vboxnote)

    # Toolbar callback funcs ############################################

    def delete_event(self, window, event):
        # don't delete; hide instead
        self.hide_on_delete()
        # self.statusicon.set_tooltip("the window is hidden")
        return True
#################################################################################

    def on_addbutton_clicked(self, widget):
        print "addnote"
        os.system(APPDIR+"/addnote.py")
#################################################################################

    def on_delbutton_clicked(self, widget):
        print "delete note"
        treeselection = self.treeviewnotes.get_selection()
        nitems = treeselection.count_selected_rows()
        if nitems == 0:
            errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error!")
            errdialog.format_secondary_text("Select a note to delete!")
            errdialog.run()
            errdialog.destroy()
        else:
            model, iter_ = treeselection.get_selected()
            # item=model.get(iter_,0)
            # group=model[iter_][0]

            title, group, filepath = model[iter_][1], model[iter_][2], model[iter_][3]
            messagedialog = Gtk.MessageDialog(message_format="Are you sure?")

            messagedialog.set_property("message-type", Gtk.MessageType.ERROR)
            messagedialog.add_button("OK", Gtk.ResponseType.OK)
            messagedialog.add_button("Cancel", Gtk.ResponseType.CANCEL)

            resp = messagedialog.run()

            if resp == Gtk.ResponseType.OK:
                self.LStr_notes.remove(iter_)
                # remove from notes db
                self.__db_delnote(title, group, filepath)

            messagedialog.destroy()
############################################################################

    def on_reloadbutton_clicked(self, widget):
        newlistagrp = self.__db_loadnotegroups()
        self.treeviewgrps.set_model(newlistagrp)
        self.__db_reloadnotes()
        self.treeviewnotes.set_model(self.LStr_notes)
############################################################################

    def on_settingsbutton_clicked(self, widget):
        global G_EVERNOTEFLAG
        global G_EVERNOTENOTEBLIST
        global G_DROPBOXFLAG
        global G_DROPBOXDIR
        global G_MINUTESFLAG
        global G_MYNOTESGEARDIR
        global G_MYNOTESGEARFLAG
        global G_REMINDERDIR
        global G_REMINDERFLAG
        global G_MINUTESFLAG
        global G_MINUTESDIR
        global G_ENCFSFLAG
        global G_ENCFSDIR

        evernnb1 = ""
        evernnb2 = ""

        dialog = Gtk.Dialog(title="Settings", buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        vboxdiag = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        listbox = Gtk.ListBox()
        listbox.set_selection_mode(Gtk.SelectionMode.NONE)

        vboxdiag.pack_start(listbox, True, True, 0)

        row = Gtk.ListBoxRow()
        hbox_drp = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_drp)

        labeldrp = Gtk.Label("", xalign=0)
        labeldrp.set_markup("<b>Dropbox Sync</b>")
        hbox_drp.pack_start(labeldrp, True, True, 0)

        switch_drp = Gtk.Switch()
        switch_drp.connect("notify::active", self.switchdrp_toggled)

        hbox_drp.pack_start(switch_drp, True, True, 0)

        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox_drp2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_drp2)

        labeldrp2 = Gtk.Label("Dropbox Folder", xalign=0)
        hbox_drp2.pack_start(labeldrp2, True, True, 0)

        self.buttondrp = Gtk.Button("Choose Folder")
        self.buttondrp.connect("clicked", self.on_drpfolder_clicked)
        hbox_drp2.pack_start(self.buttondrp, True, True, 0)

        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox_drp3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_drp3)

        labeldrp3 = Gtk.Label("Setting: ", xalign=0)
        hbox_drp3.pack_start(labeldrp3, True, True, 0)
        labeldrp4 = Gtk.Label("", xalign=0)
        hbox_drp3.pack_start(labeldrp4, True, True, 1)

        listbox.add(row)

        if G_DROPBOXFLAG == "1":
            switch_drp.set_active(True)
            self.drpfolder = G_DROPBOXDIR
            labeldrp4.set_text(G_DROPBOXDIR)
        else:
            switch_drp.set_active(False)
            self.drpfolder = ""
            self.buttondrp.set_sensitive(False)

####################################################
        row = Gtk.ListBoxRow()
        hbox_minutes = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_minutes)

        labelmin = Gtk.Label("", xalign=0)
        labelmin.set_markup("<b>Minutes Sync</b>")
        hbox_minutes.pack_start(labelmin, True, True, 0)

        switch_minutes = Gtk.Switch()
        switch_minutes.connect("notify::active", self.switchmin_toggled)

        hbox_minutes.pack_start(switch_minutes, True, True, 0)
        listbox.add(row)

        row = Gtk.ListBoxRow()

        hbox_minutes2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_minutes2)
        labelmin2 = Gtk.Label("Set Minutes Folder", xalign=0)
        hbox_minutes2.pack_start(labelmin2, True, True, 0)

        self.buttonmin = Gtk.Button("Choose Folder")
        self.buttonmin.connect("clicked", self.on_minfolder_clicked)
        hbox_minutes2.pack_start(self.buttonmin, True, True, 0)
        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox_min3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_min3)

        labelmin3 = Gtk.Label("Setting: ", xalign=0)
        hbox_min3.pack_start(labelmin3, True, True, 1)
        labelmin4 = Gtk.Label("", xalign=0)
        hbox_min3.pack_start(labelmin4, True, True, 1)

        listbox.add(row)
        if G_MINUTESFLAG == "1":
            switch_minutes.set_active(True)
            self.minfolder = G_MINUTESDIR
            labelmin4.set_text(G_MINUTESDIR)
        else:
            switch_minutes.set_active(False)
            self.minfolder = ""
            self.buttonmin.set_sensitive(False)

####################################################
        row = Gtk.ListBoxRow()
        hbox_mynotes = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_mynotes)

        labelmyn = Gtk.Label("", xalign=0)
        labelmyn.set_markup("<b>MyNotesGear Sync</b>")
        hbox_mynotes.pack_start(labelmyn, True, True, 0)

        switch_mynotes = Gtk.Switch()
        switch_mynotes.connect("notify::active", self.switchmyn_toggled)

        hbox_mynotes.pack_start(switch_mynotes, True, True, 0)
        listbox.add(row)

        row = Gtk.ListBoxRow()

        hbox_mynotes2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_mynotes2)
        labelmyn2 = Gtk.Label("Set My Notes Gear Folder", xalign=0)
        hbox_mynotes2.pack_start(labelmyn2, True, True, 0)

        self.buttonmyn = Gtk.Button("Choose Folder")
        #self.buttonmyn.connect("clicked", self.on_minfolder_clicked)
        hbox_mynotes2.pack_start(self.buttonmyn, True, True, 0)
        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox_myn3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_myn3)

        labelmyn3 = Gtk.Label("Setting: ", xalign=0)
        hbox_myn3.pack_start(labelmyn3, True, True, 1)
        labelmyn4 = Gtk.Label("", xalign=0)
        hbox_myn3.pack_start(labelmyn4, True, True, 1)

        listbox.add(row)
        if G_MYNOTESGEARFLAG == "1":
            switch_mynotes.set_active(True)
            self.mynfolder = G_MYNOTESGEARDIR
            labelmyn4.set_text(G_MYNOTESGEARDIR)
        else:
            switch_mynotes.set_active(False)
            self.mynfolder = ""
            self.buttonmyn.set_sensitive(False)

####################################################
        row = Gtk.ListBoxRow()
        hbox_encfs = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_encfs)

        labelencfs = Gtk.Label("", xalign=0)
        labelencfs.set_markup("<b>Private Sync</b>")
        hbox_encfs.pack_start(labelencfs, True, True, 0)

        switch_encfs = Gtk.Switch()
        switch_encfs.connect("notify::active", self.switchencfs_toggled)

        hbox_encfs.pack_start(switch_encfs, True, True, 0)
        listbox.add(row)

        row = Gtk.ListBoxRow()

        hbox_encfs2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_encfs2)
        labelencfs2 = Gtk.Label("Set Private Folder", xalign=0)
        hbox_encfs2.pack_start(labelencfs2, True, True, 0)

        self.buttonencfs = Gtk.Button("Choose Folder")
        self.buttonencfs.connect("clicked", self.on_encfsfolder_clicked)
        hbox_encfs2.pack_start(self.buttonencfs, True, True, 0)
        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox_encfs3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_encfs3)

        labelencfs3 = Gtk.Label("Setting: ", xalign=0)
        hbox_encfs3.pack_start(labelencfs3, True, True, 1)
        labelencfs4 = Gtk.Label("", xalign=0)
        hbox_encfs3.pack_start(labelencfs4, True, True, 1)

        listbox.add(row)
        if G_ENCFSFLAG == "1":
            switch_encfs.set_active(True)
            self.encfsfolder = G_ENCFSDIR
            labelencfs4.set_text(G_ENCFSDIR)
        else:
            switch_encfs.set_active(False)
            self.encfsfolder = ""
            self.buttonencfs.set_sensitive(False)

####################################################
        row = Gtk.ListBoxRow()
        hbox_evern1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_evern1)

        labelevern = Gtk.Label("", xalign=0)
        labelevern.set_markup("<b>Evernote Sync</b>")
        hbox_evern1.pack_start(labelevern, True, True, 0)

        switch_evern = Gtk.Switch()
        switch_evern.connect("notify::active", self.switchevern_toggled)

        hbox_evern1.pack_start(switch_evern, True, True, 0)

        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox_evern2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_evern2)
        labelevernselect1 = Gtk.Label("Notebooks Selected:", xalign=0)
        hbox_evern2.pack_start(labelevernselect1, True, True, 0)
        self.labelevernnblist = Gtk.Label("", xalign=0)
        hbox_evern2.pack_start(self.labelevernnblist, True, True, 0)

        listbox.add(row)

        row = Gtk.ListBoxRow()
        hbox_evern3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=50)
        row.add(hbox_evern3)
        labelevernselect2 = Gtk.Label("Press to select Notebooks", xalign=0)
        hbox_evern3.pack_start(labelevernselect2, True, True, 0)
        self.buttonever = Gtk.Button("Connect")
        self.buttonever.connect("clicked", self.on_buttonever_clicked)
        hbox_evern3.pack_start(self.buttonever, True, True, 0)

        listbox.add(row)

        if G_EVERNOTEFLAG == "1":
            switch_evern.set_active(True)
            if len(G_EVERNOTENOTEBLIST) > 20:
                s = G_EVERNOTENOTEBLIST[ 1 : 1 + 20] + "..."
                self.labelevernnblist.set_text(s)
            else:
                self.labelevernnblist.set_text(G_EVERNOTENOTEBLIST)
        else:
            switch_evern.set_active(False)

        box = dialog.get_content_area()
        box.add(vboxdiag)
        vboxdiag.show_all()

        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            if switch_drp.get_active():
                if G_DROPBOXFLAG == "0" and os.path.isdir(self.drpfolder):
                    G_DROPBOXFLAG = "1"
                    G_DROPBOXDIR = self.drpfolder
                    f = open(NOTEBOXCONF, "a")
                    f.write("DROPBOX=1")
                    f.write("DROPBOXDIR="+G_DROPBOXDIR)
                    f.close()
                if os.path.isdir(self.drpfolder) and self.drpfolder != G_DROPBOXDIR:
                    print "DD 1"
                    G_DROPBOXDIR = self.drpfolder
                    os.system("cat "+NOTEBOXCONF+" | grep -vE 'DROPBOXDIR=|DROPBOX=' | tee  "+NOTEBOXCONF)
                    G_DROPBOXFLAG = "1"
                    G_DROPBOXDIR = self.drpfolder
                    f = open(NOTEBOXCONF, "a")
                    f.write("DROPBOX=1\n")
                    f.write("DROPBOXDIR="+G_DROPBOXDIR+"\n")
                    f.close()

            if switch_minutes.get_active():
                if G_MINUTESFLAG == "0" and os.path.isdir(self.minfolder):
                    G_MINUTESDIR = self.minfolder
                    print "DD 2"
                    os.system("cat "+NOTEBOXCONF+" | grep -vE 'MINUTESDIR=|MINUTES=' | tee  "+NOTEBOXCONF)
                    G_MINUTESFLAG = "1"
                    G_MINUTESDIR = self.minfolder
                    f = open(NOTEBOXCONF, "a")
                    f.write("MINUTES=1\n")
                    f.write("MINUTESDIR="+G_MINUTESDIR+"\n")
                    f.close()
            if switch_evern.get_active():
                if G_EVERNOTENOTEBLIST == "":
                    G_EVERNOTEFLAG = "0"
                    print "DD 3"
                    os.system("cat "+NOTEBOXCONF+" | grep -vE 'EVERNOTENOTEBLIST=|EVERNOTE=' | tee  "+NOTEBOXCONF)
                    errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Saving settings")
                    errdialog.format_secondary_text("No Evernote notebooks selected!")
                    errdialog.run()
                    errdialog.destroy()
                else:
                    if G_EVERNOTEFLAG == "0":
                        os.system("cat "+NOTEBOXCONF+" | grep -vE 'EVERNOTENOTEBLIST=|EVERNOTE=' | tee  "+NOTEBOXCONF)
                        f = open(NOTEBOXCONF, "a")
                        f.write("EVERNOTE=1\n")
                        f.write("EVERNOTENOTEBLIST="+G_EVERNOTENOTEBLIST+"\n")
                        f.close()
        dialog.destroy()

#########################################################
    def on_findbutton_activated(self, widget):
        text = widget.get_text()

        foundlist = []

        if len(text) > 0:
            # Find in native list
            for i in range(len(self.LStr_notes)):
                # ith element in list
                path = Gtk.TreePath(i)
                treeiter = self.LStr_notes.get_iter(path)
                # Get value at 1st column
                value1 = self.LStr_notes.get_value(treeiter, 0)
                value2 = self.LStr_notes.get_value(treeiter, 1)
                value3 = self.LStr_notes.get_value(treeiter, 2)
                value4 = self.LStr_notes.get_value(treeiter, 3)
                if text.lower() in value1.lower():
                    # print "AA "+value1
                    foundlist.append([value1, value2, value3, value4])
            # Find in Minutes
            if G_MINUTESFLAG == "1" and os.path.isdir(G_MINUTESDIR):
                try:
                    output = subprocess.check_output("ls -1 "+G_MINUTESDIR+"/*.txt", shell=True)
                    tmplist = output.split("\n")
                    for item in tmplist:
                        if item != "":
                            header = ""
                            try:
                                header = subprocess.check_output("cat '"+item+"' | head -3 ", shell=True)
                            except:
                                header = ""
                            if text.lower() in header.lower():
                                # self.LStr_notes.append(["** "+basename(item)+"** \n"+header,basename(item),"Minutes",item])
                                foundlist.append(["** "+basename(item)+"** \n"+header, basename(item), "Minutes", item])
                except:
                    print "No notes in Minutes"
            # Find in Private
            if G_ENCFSFLAG == "1" and os.path.isdir(G_ENCFSDIR):
                try:
                    output = subprocess.check_output("ls -1 "+G_ENCFSDIR+"/*.txt", shell=True)
                    tmplist = output.split("\n")
                    for item in tmplist:
                        if item != "":
                            header = ""
                            try:
                                header = subprocess.check_output("cat '"+item+"' | head -3 ", shell=True)
                            except:
                                header = ""
                            if text.lower() in header.lower():
                                # self.LStr_notes.append(["** "+basename(item)+"** \n"+header,basename(item),"Minutes",item])
                                foundlist.append(["** "+basename(item)+"** \n"+header, basename(item), "Private", item])
                except:
                    print "No notes in Encripted directory Private"

            # recreate liststore with ocurrences
            if len(foundlist) == 0:
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Attention!")
                errdialog.format_secondary_text("Can't find string in note list!")
                errdialog.run()
                errdialog.destroy()
            else:
                self.LStr_notes.clear()
                for item in foundlist:
                    self.LStr_notes.append([item[0], item[1], item[2], item[3]])

#########################################################
    def on_drpfolder_clicked(self, widget):
        dialog = Gtk.FileChooserDialog("Dropbox folder", self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # print("Select clicked")
            self.drpfolder = dialog.get_filename()
        dialog.destroy()
#########################################################

    def on_minfolder_clicked(self, widget):
        global G_MINUTEDIR
        global HomeDir
        dialog = Gtk.FileChooserDialog("Set Minutes folder", self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        dialog.set_filename(HomeDir)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # print("Select clicked")
            minfolder = dialog.get_filename()
            if minfolder != "" and os.path.isdir(minfolder):
                os.system(APPDIR+"/setupminutes.sh "+minfolder+" "+G_MINUTEDIR)
        dialog.destroy()

#########################################################
    def on_mynfolder_clicked(self, widget):
        global G_MYNOTESGEARDIR
        global HomeDir
        dialog = Gtk.FileChooserDialog("Set My Notes folder", self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        dialog.set_filename(HomeDir)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # print("Select clicked")
            mynfolder = dialog.get_filename()
            if mynfolder != "" and os.path.isdir(mynfolder):
                os.system(APPDIR+"/setupmynotesgear.sh "+mynfolder+" "+G_MYNOTESGEARDIR)
        dialog.destroy()

#########################################################
    def on_encfsfolder_clicked(self, widget):
        global G_ENCFSDIR
        global HomeDir
        dialog = Gtk.FileChooserDialog("Set Private folder", self,
            Gtk.FileChooserAction.SELECT_FOLDER,
            (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
             "Select", Gtk.ResponseType.OK))
        dialog.set_default_size(800, 400)
        dialog.set_filename(HomeDir)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            # print("Select clicked")
            encfsfolder = dialog.get_filename()
            if encfsfolder != "" and os.path.isdir(encfsfolder):
                os.system(APPDIR+"/setupencfs.sh "+encfsfolder+" "+G_ENCFSDIR)
        dialog.destroy()
#########################################################

    def switchdrp_toggled(self, switch, state):
        if switch.get_active():
            self.buttondrp.set_sensitive(True)

        else:
            self.buttondrp.set_sensitive(False)
#########################################################

    def switchmin_toggled(self, switch, state):
        if switch.get_active():
            self.buttonmin.set_sensitive(True)

        else:
            self.buttonmin.set_sensitive(False)

#########################################################
    def switchmyn_toggled(self, switch, state):
        if switch.get_active():
            self.buttonmyn.set_sensitive(True)
        else:
            self.buttonmyn.set_sensitive(False)

#########################################################

    def switchencfs_toggled(self, switch, state):
        if switch.get_active():
            self.buttonencfs.set_sensitive(True)

        else:
            self.buttonencfs.set_sensitive(False)
# #####Right menu ########################

    def on_treeviegrp_event(self, widget, event):
        print "aa"
        time = event.time
        if event.button == 3:
            self.rmenu.popup(None, None, None, None, event.button, time)
            self.rmenu.show_all()
############################################

    def on_menuren(self, widget):
        treesel = self.treeviewgrps.get_selection()
        model, iter_ = treesel.get_selected()
        item = model.get(iter_, 0)
        group = model[iter_][0]
        grptype = model[iter_][2]

        if grptype == "folder":
            messagedialog = Gtk.MessageDialog(message_format="Rename note group "+group+"? \nAre you sure?")

            messagedialog.set_property("message-type", Gtk.MessageType.ERROR)
            messagedialog.add_button("OK", Gtk.ResponseType.OK)
            messagedialog.add_button("Cancel", Gtk.ResponseType.CANCEL)

            resp = messagedialog.run()
            if resp == Gtk.ResponseType.OK:
                self.__db_rennotegroup(group, iter_)


#####################################################
    def on_menudel(self, widget):
        treesel = self.treeviewgrps.get_selection()
        model, iter_ = treesel.get_selected()
        item = model.get(iter_, 0)
        group = model[iter_][0]
        grptype = model[iter_][2]

        if group != "Add Group..." and grptype != "evernote" and grptype != "reminders" and grptype != "minutes" and grptype != "private":
            print "Siiii"
            messagedialog = Gtk.MessageDialog(message_format="Delete note group "+group+"? \nAll notes in this group will be deleted too!")

            messagedialog.set_property("message-type", Gtk.MessageType.ERROR)
            messagedialog.add_button("OK", Gtk.ResponseType.OK)
            messagedialog.add_button("Cancel", Gtk.ResponseType.CANCEL)

            resp = messagedialog.run()
            if resp == Gtk.ResponseType.OK:

                # remove from listore
                # self.LStr_notes.remove(treeiter)
                self.LStr_grps.remove(iter_)

                # remove group from db
                self.__db_delgrp(group)
                # remove notes for this group
                self.__db_delnotesbygrp(group)

                newlistagrp = self.__db_loadnotegroups()
                self.treeviewgrps.set_model(newlistagrp)
                self.__db_reloadnotes()
                self.treeviewnotes.set_model(self.LStr_notes)

            messagedialog.destroy()
        else:
            errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error!")
            errdialog.format_secondary_text("Group cannot be deleted!")
            errdialog.run()
            errdialog.destroy()

    def on_buttonever_clicked(self, widget):
        global G_EVERNOTENOTEBLIST
        global NOTEBOXCONF

        dialog = Gtk.Dialog(title="Select Evernote Notebooks", buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        vboxdiag = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)

        nbliststr = Gtk.ListStore(str)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.set_size_request(300, 200)

        treelist = Gtk.TreeView(model=nbliststr)
        treeviewcolumn = Gtk.TreeViewColumn("Notebooks")
        treelist.append_column(treeviewcolumn)
        treelist.connect("row-activated", self.on_notebooklist_activated)
        cellrenderertext = Gtk.CellRendererText()
        treeviewcolumn.pack_start(cellrenderertext, True)
        treeviewcolumn.add_attribute(cellrenderertext, "text", 0)

        treeselection = treelist.get_selection()
        treeselection.set_mode(3)  # Multiple

        scroll.add(treelist)
        vboxdiag.pack_start(scroll, True, True, 0)

        box = dialog.get_content_area()
        box.add(vboxdiag)
        vboxdiag.show_all()

        try:
            os.system("zenity --progress --pulsate --title 'Connecting to Evernote' &")
            socket.setdefaulttimeout(3)
            conn = httplib.HTTPConnection('www.evernote.com')  # I used here HTTP not HTTPS for simplify
            conn.request('HEAD', '/')  # Just send a HTTP HEAD request
            res = conn.getresponse()

            content = subprocess.check_output("geeknote notebook-list | grep -v Total | cut -d: -f 2", shell=True)
        except:
            os.system("killall zenity &")
            content = ""
            errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Connecting to Evernote")
            errdialog.format_secondary_text("Error obtaining notebook list!")
            errdialog.run()
            errdialog.destroy()

        nblist = content.split("\n")

        if len(nblist) > 0:
            for item in nblist:
                nbliststr.append([item.lstrip(" ")])
            os.system("killall zenity &")
            response = dialog.run()
            if response == Gtk.ResponseType.OK:
                (model, pathlist) = treeselection.get_selected_rows()
                nblist = ""
                i = 0
                for item in pathlist:
                    print model[item][0]
                    if i == 0:
                        nblist = model[item][0]
                    else:
                        nblist = nblist+","+model[item][0]
                    i = i+1
                if nblist != "":
                    if nblist != G_EVERNOTENOTEBLIST:
                        G_EVERNOTENOTEBLIST = nblist
                        os.system("cat "+NOTEBOXCONF+" | grep -vE 'EVERNOTENOTEBLIST=|EVERNOTE=' | tee  "+NOTEBOXCONF)
                        f = open(NOTEBOXCONF, "a")
                        f.write("EVERNOTE=1\n")
                        f.write("EVERNOTENOTEBLIST="+G_EVERNOTENOTEBLIST)+"\n"
                        f.close()
                        self.labelevernnblist.set_text(G_EVERNOTENOTEBLIST)
                else:
                    errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error in notebook list")
                    errdialog.format_secondary_text("List is empty. Please select notebooks!")
                    errdialog.run()
                    errdialog.destroy()

        dialog.destroy()


#########################################################
    def on_notebooklist_activated(self, widget, path, column):
        print "add group"

    def switchevern_toggled(self, switch, state):
        if switch.get_active():
            self.buttonever.set_sensitive(True)
        else:
            self.buttonever.set_sensitive(False)

    def on_addgrpbutton_clicked(self, widget):
        print "add group"

# ##### Lists Callbacks ################################################
    def on_treeviewgrp_activated(self, widget, path, column):
        print "row activated "
        treesel = self.treeviewgrps.get_selection()
        model, iter_= treesel.get_selected()
        item = model.get(iter_, 0)
        group = model[iter_][0]
        grptype = model[iter_][2]
        if group == "Add Group...":
            self.__db_addnotegroup()
        else:
            print "XX "+group + " - " + grptype
            self.__db_loadnotesbygrp(group, grptype)

#####################################################################

    def on_treeviewnote_activated(self, widget, path, column):
        print "row activated: "
        treesel = self.treeviewnotes.get_selection()
        model, iter_ = treesel.get_selected()
        item = model.get(iter_, 0)
        title, group, filepath = model[iter_][1], model[iter_][2], model[iter_][3]
        # print model[iter_][0]+"--"+model[iter_][1]+"--"+model[iter_][2]
        print APPDIR+"/opennote.py -t '"+title+"' -g "+group+" -f \""+filepath+"\""
        os.system(APPDIR+"/opennote.py -t '"+title+"' -g "+group+" -f \""+filepath+"\" &")


    #Low level Utility funcs ###################################################

    def __db_rennotegroup(self, group, pos):
        global APP
        print ""
        dialog = Gtk.Dialog(title="Rename Group", buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        vboxdiag = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        entrygrp = Gtk.Entry()
        entrygrp.set_text("Group Name")
        vboxdiag.pack_start(entrygrp, True, True, 0)
        box = dialog.get_content_area()
        box.add(vboxdiag)
        vboxdiag.show_all()
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            groupname = entrygrp.get_text()
            if groupname == "":
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error Creating Group")
                errdialog.format_secondary_text("No name specified!")
                errdialog.run()
                errdialog.destroy()
            elif groupname == "Minutes" or groupname == "Private":
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error Creating Group")
                errdialog.format_secondary_text("Group name is reserved. Try another one!")
                errdialog.run()
                errdialog.destroy()
            elif os.path.isdir(BASEDIR+"/"+groupname):
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error Creating Group")
                errdialog.format_secondary_text("Group already exists!")
                errdialog.run()
                errdialog.destroy()
            else:
                result = os.system("mkdir "+BASEDIR+"/"+group)
                if result == 0:
                    self.LStr_grps.insert(pos, [group, "folder", "folder"])
                    seld.LStr_grps.remove(pos)

                else:
                    notif_msg(APP, "Error Renaming group "+group)

    # Low level Utility funcs ##################################################

    def __db_addnotegroup(self):
        global APP
        print ""
        dialog = Gtk.Dialog(title="Creating Group", buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        vboxdiag = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        entrygrp = Gtk.Entry()
        entrygrp.set_text("Group Name")
        vboxdiag.pack_start(entrygrp, True, True, 0)
        box = dialog.get_content_area()
        box.add(vboxdiag)
        vboxdiag.show_all()
        response = dialog.run()

        if response == Gtk.ResponseType.OK:
            groupname = entrygrp.get_text()
            if groupname == "":
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error Creating Group")
                errdialog.format_secondary_text("No name specified!")
                errdialog.run()
                errdialog.destroy()
            elif groupname == "Minutes" or groupname == "Private":
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error Creating Group")
                errdialog.format_secondary_text("Group name is reserved. Try another one!")
                errdialog.run()
                errdialog.destroy()
            elif os.path.isdir(BASEDIR+"/"+groupname):
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Error Creating Group")
                errdialog.format_secondary_text("Group already exists!")
                errdialog.run()
                errdialog.destroy()
            else:
                result = os.system("mkdir "+BASEDIR+"/"+groupname)
                if result == 0:
                    self.LStr_grps.append([groupname, "folder", "folder"])

                    # self.__db_loadnotegroups()
                else:
                    notif_msg(APP, "Error creating group "+groupname)

        dialog.destroy()


###################################################################
    def __db_delgrp(self, group):
        if group != "":
            cmd = "rm -rf "+BASEDIR+"/"+group
            os.system(cmd)

###################################################################
    def __db_loadnotegroups(self):
        global G_EVERNOTENOTEBLIST
        try:
            output = subprocess.check_output("ls -1d "+BASEDIR+"/* | grep -v dat", shell=True)
        except:
            output = ""
        # del self.grplist[:]

        tmplist = output.split("\n")
        if len(tmplist) == 0:
            print "No groups in list. Error in config file"
            sys.exit(2)

        # self.LStr_grps.clear()
        newlist = Gtk.ListStore(str, str, str)
        # self.grplist.append("Add Group...")
        # self.LStr_grps.append(["Add Group...","blank","Add"])

        newlist.append(["Add Group...", "blank", "Add"])

        if G_EVERNOTEFLAG == "1":
            nbs = G_EVERNOTENOTEBLIST
            nblist = nbs.split(",")
            for item in nblist:
                newlist.append([item, "evernote", "evernote"])

        for item in tmplist:
            if item != "":
                newlist.append([basename(item), "folder", "folder"])

        if G_MYNOTESGEARFLAG == "1":
            newlist.append(["MyNotesGear", "mynotesgearimg", "mynotesgear"])

        if G_MINUTESFLAG == "1":
            newlist.append(["Minutes", "minutes", "minutes"])

        if G_REMINDERFLAG == "1":
            newlist.append(["Reminders", "reminders", "reminders"])

        if G_ENCFSFLAG == "1":
            newlist.append(["Private", "nb_lock", "private"])

        return newlist
###################################################################

    def __db_reloadnotes(self):
        del self.notelist[:]
        del self.sortnotelist[:]

        self.LStr_notes.clear()

        # Load notes from db file
        f = open(G_NOTESDAT, "r")
        values = []
        notelist = []
        for line in f:
            line2 = line
            line2.rstrip('\n')
            if line2 != "":
                values = line2.split(";")
                header = ""
                try:
                    header = subprocess.check_output("cat '"+BASEDIR+"/"+values[2]+"' | head -3 ", shell=True)
                except:
                    header = ""
                n = notes(values[0], values[1], values[2], values[3], header)
                self.notelist.append(n)
                notelist.append([n.title, n.group, n.notestamp, n.notefile, n.header, "folder"])
                # self.LStr_notes.append([n.title])
        f.close()

         # ####Load Private notes
        # if G_ENCFSFLAG=="1" and os.path.isdir(G_ENCFSDIR):
            # try:
                # output = subprocess.check_output("ls -1 "+G_ENCFSDIR+"/*.txt", shell=True)
                # tmplist=output.split("\n")
                # for item in tmplist:
                    #i f item != "":
                        # header=""
                        # try:
                            # header=subprocess.check_output("cat '"+item+"' | head -3 ", shell=True)
                        # except:
                            # header=""
                        # n=notes(basename(item)+"\n"+header,"Private",item,int(time.time()),header)
                        # self.notelist.append(n)
                        # #self.LStr_notes.append([n.title])
                        # notelist.append([n.title,n.group,n.notestamp,item,n.header])
            #e xcept:
                 # print "No notes in Private Dir"
        self.sortnotelist = sorted(notelist, key=getKey, reverse=True)
        for item in  self.sortnotelist:
            #print "CC "+item[0]+"-"+item[1]+"-"+item[3]+"--"+item[2]
            self.LStr_notes.append(["** "+item[0]+" **\n"+item[4], item[0], item[1], item[3]])

################################################################
    def __db_delnotesbygrp(self, group):
        os.system("cp -p "+G_NOTESDAT+" /tmp/notebox.dat")
        w = open(G_NOTESDAT, "w")
        with open("/tmp/notebox.dat", "r") as f:
            for line in f:
                if len(line) > 0:
                    values = line.split(';')
                    if values[1] != group:
                        w.write(line)
        w.close()
################################################################
    ###xxx
    def __db_delnote(self, title, group, filepath):
        if group == "Minutes" or group == "Reminders" or group == "Private" or group == "MyNotesGear":
            print "About to remove Minutes note: "+filepath
            os.remove(filepath)
        elif filepath == "evernote":
            print "About to delete note from Evernote notebook"
        else:
            print "erasing native note "+title+" - "+filepath
            i = 0
            os.system("cp -p "+G_NOTESDAT+" /tmp/notebox.dat")
            w = open(G_NOTESDAT, "w")
            for item in self.sortnotelist:
                print "       found note!"
                if item[0] == title and item[1] == group:
                    del self.sortnotelist[i]

                    with open("/tmp/notebox.dat", "r") as f:
                        for line in f:
                            if len(line) > 0:
                                values = line.split(';')
                                if values[0] != title:
                                    w.write(line)
                    w.close()
                    print "returning true..."
                    return(True)
                i = i+1
            w.close()
            print "returning false..."
            return (False)
###################################################################

    def __db_loadnotesbygrp(self, grp, grptype):

        self.LStr_notes.clear()
        # ####Load Minutes notes
        if grptype == "minutes" and os.path.isdir(G_MINUTESDIR):
            try:
                output = subprocess.check_output("ls -1 "+G_MINUTESDIR+"/*.txt", shell=True)
                tmplist = output.split("\n")
                for item in tmplist:
                    if item != "":
                        header = ""
                        try:
                            header = subprocess.check_output("cat '"+item+"' | head -3 ", shell=True)
                        except:
                            header = ""
                        # n=notes(basename(item),"Minutes",item,int(time.time()),header)
                        # self.notelist.append(n)
                        self.LStr_notes.append(["** "+basename(item)+"** \n"+header, basename(item), "Minutes", item])
                        # notelist.append([n.title,n.group,n.notestamp,item,header])
            except:
                print "No notes in Minutes"

        # #### Load MytNotesGear notes
        if grptype == "mynotesgear" and os.path.isdir(G_MYNOTESGEARDIR):
            try:
                output = subprocess.check_output("ls -1r "+G_MYNOTESGEARDIR, shell=True)
                tmplist = output.split("\n")
                for item in tmplist:
                    if item != "":
                        header = ""

                        ntitle = subprocess.check_output("grep note_Title " + G_MYNOTESGEARDIR+"/"+item+" | cut -d: -f 2 |  tr -d \\\" | tr -d ,", shell=True)
                        ntitle = ntitle.strip("\n")
                        nisarchived = subprocess.check_output("grep Isarchived " + G_MYNOTESGEARDIR+"/"+item+" | cut -d: -f 2 ", shell=True)
                        nisarchived = nisarchived.strip("\n")
                        print "AA "+ntitle + "--"+nisarchived
                        # title+header,title,group,filepath o evernote
                        if nisarchived == " false,":
                            self.LStr_notes.append(["** "+ntitle.lstrip(" ")+" **", ntitle.lstrip(" "), "MyNotesGear", G_MYNOTESGEARDIR+"/"+item])

            except:
                print "No notes in MyNotesGear"
        # #### Load Reminders notes
        if grptype == "reminders" and os.path.isdir(G_REMINDERDIR):
            try:
                output = subprocess.check_output("ls -1r "+G_REMINDERDIR, shell=True)
                tmplist = output.split("\n")
                for item in tmplist:
                    if item != "":
                        header = ""
                        ntitle = subprocess.check_output("cat \"" + G_REMINDERDIR+"/"+item+"\"", shell=True)
                        ntitle = ntitle.strip("\n")
                        self.LStr_notes.append(["** "+ntitle.lstrip(" ")+" **", ntitle.lstrip(" "), "Reminders", G_REMINDERDIR+"/"+item])

            except:
                print "No notes in Reminder dir"
        # ####Load Private notes
        # print "AA "+G_ENCFSDIR+"-"+grptype+"--"
        if grptype == "private" and os.path.isdir(G_ENCFSDIR):
            try:
                output = subprocess.check_output("ls -1 "+G_ENCFSDIR+"/*", shell=True)
                tmplist = output.split("\n")
                for item in tmplist:
                    if item != "":
                        header = ""
                        try:
                            header = subprocess.check_output("cat '"+item+"' | head -3 ", shell=True)
                        except:
                            header = ""
                        # n=notes(basename(item),"Minutes",item,int(time.time()),header)
                        # self.notelist.append(n)
                        self.LStr_notes.append(["** "+basename(item)+"** \n"+header, basename(item), "Private", item])
                        print "DD item: ", item
                        # notelist.append([n.title,n.group,n.notestamp,item,header])
            except:
                print "No notes in Private"
        elif grptype == "evernote":
            socket.setdefaulttimeout(5)

            try:
                print "Evernote !!!"

                os.system("zenity --progress --pulsate --title 'Connecting to Evernote' &")
                conn = httplib.HTTPConnection('www.evernote.com')  # I used here HTTP not HTTPS for simplify
                conn.request('HEAD', '/')  # Just send a HTTP HEAD request
                res = conn.getresponse()

                output = subprocess.check_output("geeknote find --search '*' --notebooks "+grp+" | grep 1970 | tr -s ' '", shell=True)

                tmplist = output.split("\n")

                self.LStr_notes.clear()
                for item in tmplist:
                    if item != "":
                        tmplist2 = item.split("1970")

                        evertitle = tmplist2[1].lstrip()
                        self.LStr_notes.append([evertitle, evertitle, grp, "evernote"])
                os.system("killall zenity &")
            except:
                os.system("killall zenity &")
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Loading Evernote Notes")
                errdialog.format_secondary_text("Cannot connect to evernote!")
                errdialog.run()
                errdialog.destroy()

        else:

            for item in self.sortnotelist:
                # if item[1] == grp or grp == "All Notes":
                if item[1] == grp:
                    self.LStr_notes.append(["** "+item[0]+"** \n"+item[4], item[0], item[1], item[3]])
###########################################################################


def cbk_shownotes(widget):
    global note
    note.show_all()


def cbk_addnote(widget):
    os.system(APPDIR+"/addnote.py &")


def cbk_quit(widget):
    Gtk.main_quit()


def cbk_about(widget):
    print "About"

# ---------------------------------------------------------------------------------------


note = MyWindow()


# print "main "+G_ENCFSDIR+"--"+G_MINUTESDIR
# sys.exit(0)
# note.connect("delete-event", Gtk.main_quit)
ind = appindicator.Indicator.new("Notebox", "notebox", appindicator.IndicatorCategory.APPLICATION_STATUS)
ind.set_icon_theme_path(APPDIR)
ind.set_status(appindicator.IndicatorStatus.ACTIVE)

menu = Gtk.Menu()
show_item = Gtk.MenuItem("Show Notes")
show_item.connect("activate", cbk_shownotes)

add_item = Gtk.MenuItem("Add Note")
add_item.connect("activate", cbk_addnote)
about_item = Gtk.MenuItem("About")
about_item.connect("activate", cbk_about)
separator = Gtk.SeparatorMenuItem()
quit_item = Gtk.MenuItem("Quit")
quit_item.connect("activate", cbk_quit)

show_item.show()
add_item.show()
about_item.show()
separator.show()
quit_item.show()
menu.show_all()

menu.append(show_item)
menu.append(add_item)
menu.append(about_item)
menu.append(separator)
menu.append(quit_item)
ind.set_menu(menu)

# Register app in the notification library
Notify.init("Notebox")
# note.connect("delete-event", note.hide)
# note.show_all()
Gtk.main()
