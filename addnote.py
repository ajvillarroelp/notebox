#!/usr/bin/python
import os
import sys
import string
import time
import subprocess
import uuid
import gi
from gi.repository import Gtk
from gi.repository import Gio
from gi.repository import Gdk
from gi.repository import Notify
from os.path import basename

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')


#########################################################


def generate_random_string(string_length=11):
    """Returns a random string of length string_length."""
    random = str(uuid.uuid4())  # Convert UUID format to a Python string.
    # random = random.upper()  # Make all characters uppercase.
    random = random.replace("-", "")  # Remove the UUID '-'.
    return random[0:string_length]  # Return the random string.
#########################################################


def notif_msg(app, msg):
    # icon = APPDIR+"/notebox.png"
    # os.system("notify-send -i "+icon+" Notebox \""+msg+"\"")
    n = Notify.Notification.new("<b>" + APP + "</b>", msg, "")
    n.show()

##########################################################


G_MARGIN = 5
HomeDir = os.environ['HOME']
NOTEBOXCONF = HomeDir + "/.notebox/notebox.conf"
BASEDIR = HomeDir + "/.notebox/notes"
APP = "Notebox"
APPDIR = HomeDir + "/.notebox"
G_NOTESDAT = ""
filename = ""
group = ""

############################################################


class MyWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="")
        self.set_icon_from_file(APPDIR + "/notes.png")

        self.set_default_size(500, 500)
        self.set_border_width(0)
        self.NOTEBOXCONF = HomeDir + "/.notebox/notebox.conf"
        self.G_NOTETITLE = ""
        self.G_NOTEFILE = ""
        self.G_NOTEGRP = ""
        self.G_EVERNOTEFLAG = "0"
        self.G_EVERNOTENOTEBLIST = ""
        self.G_DROPBOXFLAG = "0"
        self.G_DROPBOXDIR = ""
        self.G_MINUTESFLAG = "0"
        self.G_MINUTESDIR = ""
        self.G_REMINDERDIR = ""
        self.G_REMINDERFLAG = "0"
        self.G_MYNOTESGEARFLAG = "0"
        self.G_MYNOTESGEARDIR = ""
        self.G_ENCFSFLAG = "0"
        self.G_ENCFSDIR = ""

        #######################
        # Read config file

        try:
            G_NOTESDAT = subprocess.check_output("grep NOTEDB " + NOTEBOXCONF + " | cut -d= -f 2", shell=True)
        except:
            G_NOTESDAT = BASEDIR + "/notebox.dat"
        G_NOTESDAT = G_NOTESDAT.rstrip('\n')

        try:
            self.G_EVERNOTEFLAG = subprocess.check_output("grep EVERNOTE " + self.NOTEBOXCONF + " | cut -d= -f 2", shell=True)
        except:
            self.G_EVERNOTEFLAG = "0"
        self.G_EVERNOTEFLAG = self.G_EVERNOTEFLAG.rstrip('\n')

        try:
            self.G_EVERNOTENOTEBLIST = subprocess.check_output("grep EVERNOTENOTEBLIST " + self.NOTEBOXCONF + " | cut -d= -f 2", shell=True)
        except:
            self.G_EVERNOTENOTEBLIST = ""
        self.G_EVERNOTENOTEBLIST = self.G_EVERNOTENOTEBLIST.rstrip('\n')

        try:
            self.G_DROPBOXFLAG = subprocess.check_output("grep -c DROPBOX=1 " + self.NOTEBOXCONF, shell=True)
        except:
            self.G_DROPBOXFLAG = "0"

        self.G_DROPBOXFLAG = self.G_DROPBOXFLAG.rstrip('\n')

        if self.G_DROPBOXFLAG == "1":
            try:
                self.G_DROPBOXDIR = subprocess.check_output("grep DROPBOXDIR " + self.NOTEBOXCONF + " | cut -d= -f 2", shell=True)
            except:
                dummy = None

            self.G_DROPBOXDIR = self.G_DROPBOXDIR.rstrip('\n')
            if not os.path.isdir(self.G_DROPBOXDIR):
                print "Cannot access Dropbox directory. Ignoring"
                self.G_DROPBOXFLAG = "0"

        try:
            self.G_MINUTESFLAG = subprocess.check_output("grep -c MINUTES=1 " + self.NOTEBOXCONF, shell=True)
        except:
            self.G_MINUTESFLAG = "0"

        self.G_MINUTESFLAG = self.G_MINUTESFLAG.rstrip('\n')
        if self.G_MINUTESFLAG == "1":
            try:
                self.G_MINUTESDIR = subprocess.check_output("grep MINUTESDIR " + self.NOTEBOXCONF + "|cut -d= -f 2 ", shell=True)
            except:
                dummy = None

            self.G_MINUTESDIR = self.G_MINUTESDIR.rstrip('\n')
            if not os.path.isdir(self.G_MINUTESDIR):
                print "Cannot access Minutes directory. Ignoring..."
                self.G_MINUTESFLAG = "0"

        try:
            self.G_MYNOTESGEARFLAG = subprocess.check_output("grep -c MYNOTESGEAR=1 " + self.NOTEBOXCONF, shell=True)
            self.G_MYNOTESGEARFLAG = self.G_MYNOTESGEARFLAG.rstrip('\n')
            self.G_MYNOTESGEARDIR = subprocess.check_output("grep MYNOTESGEARDIR " + self.NOTEBOXCONF + "|cut -d= -f 2 ", shell=True)
            self.G_MYNOTESGEARDIR = self.G_MYNOTESGEARDIR.rstrip('\n')
        except:
            self.G_MYNOTESGEARFLAG = "0"

        try:
            self.G_ENCFSFLAG = subprocess.check_output("grep -c ENCFS=1 " + self.NOTEBOXCONF, shell=True)
        except:
            dummy = None

        try:
            self.G_REMINDERFLAG = subprocess.check_output("grep -c REMINDER=1 " + self.NOTEBOXCONF, shell=True)
            self.G_REMINDERFLAG = self.G_REMINDERFLAG.rstrip('\n')
            self.G_REMINDERDIR = subprocess.check_output("grep REMINDERDIR " + self.NOTEBOXCONF + "|cut -d= -f 2 ", shell=True)
            self.G_REMINDERDIR = self.G_REMINDERDIR.rstrip('\n')
        except:
            self.G_REMINDERFLAG = "0"

        try:
            self.G_ENCFSFLAG = subprocess.check_output("grep -c ENCFS=1 " + self.NOTEBOXCONF, shell=True)
        except:
            dummy = None

        self.G_ENCFSFLAG = self.G_ENCFSFLAG.rstrip('\n')
        if self.G_ENCFSFLAG == "1":
            try:
                self.G_ENCFSDIR = subprocess.check_output("grep ENCFSDIR " + self.NOTEBOXCONF + "|cut -d= -f 2 ", shell=True)
                print "AA ", self.G_ENCFSDIR
            except:
                dummy = None
                print "dummmy ", self.G_ENCFSDIR
            self.G_ENCFSDIR = self.G_ENCFSDIR.rstrip('\n')
            if self.G_ENCFSDIR == "":
                self.G_ENCFSFLAG = "0"

        #######################

        self.LStr_grps = Gtk.ListStore(str, str, str)
        self.LStr_grps = self.__db_loadnotegroups()

        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

        # Window content Header bar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Add Note"
        # hb.set_subtitle(grp)

        self.set_titlebar(hb)

        self.savebutton = Gtk.Button()
        self.savebutton.connect("clicked", self.on_savebutton_clicked)
        self.savebutton.set_tooltip_text("Save Note")
        icon = Gio.ThemedIcon(name="document-save")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.savebutton.add(image)
        hb.pack_start(self.savebutton)

        self.wrapbutton = Gtk.ToggleButton()

        self.wrapbutton.connect("toggled", self.on_wrapbutton_clicked)
        self.wrapbutton.set_tooltip_text("Wrap text")
        self.wrapbutton.set_active(True)
        icon = Gio.ThemedIcon(name="view-wrapped-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.wrapbutton.add(image)
        hb.pack_start(self.wrapbutton)

        vboxnote = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=1)
        Gtk.StyleContext.add_class(vboxnote.get_style_context(), "linked")
        hb.pack_start(vboxnote)

        vboxnote2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.noteview = Gtk.TextView()
        self.noteview.set_border_window_size(Gtk.TextWindowType.LEFT, G_MARGIN)
        self.noteview.set_border_window_size(Gtk.TextWindowType.RIGHT, G_MARGIN)
        self.noteview.set_border_window_size(Gtk.TextWindowType.TOP, G_MARGIN)
        self.noteview.set_border_window_size(Gtk.TextWindowType.BOTTOM, G_MARGIN)
        self.noteview.set_wrap_mode(True)
        self.noteview.set_size_request(300, 300)

        textbuffer = self.noteview.get_buffer()

        content = self.clipboard.wait_for_text()
        if content is not None:
            textbuffer.set_text(content)

        scroll.add(self.noteview)
        vboxnote2.pack_start(scroll, True, True, 0)
        # self.add(scroll)
        self.add(vboxnote2)

##############################################################################


    def mynotesgearsave(self, content, filepath):
        os.system("cp -p " + filepath + " /tmp")
        w = open(filepath, "w")
        # split  new lines to remove from content
        content_list = content.split('\n')
        with open("/tmp/" + basename(filepath), "r") as f:
            for line in f:
                # line = line.rstrip("\n")
                if len(line) > 0:
                    if line.find("note_Notes") > 0:
                        w.write(" \"note_Notes\": \"")
                        nitem = 1
                        for item in content_list:
                            if len(item) > 0:
                                if nitem == 1:
                                    w.write(item)
                                else:
                                    w.write("\\n" + item)
                                nitem = nitem + 1
                        w.write("\",")
                        # print line + "-- "
                    else:
                        # w.write(line+"\n")
                        w.write(line)
        w.close()

#############################################################

    def __db_savenote(self, title, grp, filepath, content, savemode):
        global APP
        # Save the note content################################################
        if grp != "Minutes" and grp != "Private" and grp != "MyNotesGear":
            # f = codecs.open(BASEDIR+"/"+notefile,"w",'utf-8')
            f = open(BASEDIR + "/" + self.G_NOTEFILE, "w")
            f.write(content)
            f.close()
            currtime = int(time.time())
            notif_msg(APP, "Saving note " + self.G_NOTETITLE)
            if savemode == "create":
                datfile = open(G_NOTESDAT, 'a')
                line = self.G_NOTETITLE + ";" + grp + ";" + self.G_NOTEFILE + ";" + str(currtime) + "\n"
                datfile.write(line)
                datfile.close()
        elif grp == "MyNotesGear":
            if savemode == "create":
                # Get the timestamp from the file path
                arrcurrtime = filepath.split("/")
                currtime = arrcurrtime[len(arrcurrtime) - 1]
                template_note = '{ "note_Id": ' + currtime + ',' + "\n" + ' "note_Alarmid": 0,' + "\n" + ' "note_Due": 0,'+"\n"+' "note_Lastedit": '+currtime+','+"\n"+' "note_Issynced": false,'+"\n"+' "note_Isedited": true,'+"\n"+' "note_Isdropboxsynced": true,'+"\n"+' "note_Isdropboxedited": true,'+"\n"+' "note_SharedUrl": "",'+"\n"+' "note_Label": "[]",'+"\n"+' "note_Position": 2097151.5,'+"\n"+' "note_Title": "'+self.G_NOTETITLE+'",'+"\n"+' "note_Notes": " '
                arraynote = content.split("\n")
                for i in arraynote:
                    template_note = template_note + i + '\n'
                template_note = template_note[:-1] + '",'+"\n"+' "note_Color": "#2196F3",'+"\n"+' "note_Istimeactive": false,'+"\n"+' "note_Islocationactive": false,'+"\n"+' "note_Isarchived": false,'+"\n"+' "note_Isdeleted": false,'+"\n"+' "note_Ischecklist": false,'+"\n"+' "note_Isshared": false,'+"\n"+' "note_Hasfile": false,'+"\n"+' "note_Filepath": "",'+"\n"+' "note_Image": "",'+"\n"+' "note_Address": "",'+"\n"
                template_note = template_note+' "note_Longitude": 0,'+"\n"+' "note_Latitude": 0,'+"\n"+' "note_FieldS1": "",'+"\n"+' "note_FieldS2": "",'+"\n"+' "note_FieldL1": 0,'+"\n"+' "note_FieldL2": 0,'+"\n"+' "note_FieldB1": false,'+"\n"+' "note_FieldB2": false'+"\n"+'}'
                notif_msg(APP, "Saving note "+self.G_NOTETITLE)
                f = open(self.G_NOTEFILE, "w")
                f.write(template_note)
                f.close()
            else:
                # notif_msg(APP, "Save mode not supported for "+self.G_NOTETITLE)
                self.mynotesgearsave(content, self.G_NOTEFILE)
                # os.system("sed -i 's/\( \"note_Notes\": \"\).*\(\"\)/ \"note_Notes\": \""+content+"\"/' "+self.G_NOTEFILE)
                notif_msg(APP, "Note "+title+" Saved!")
                return
        else:
            notif_msg(APP, "Saving note "+self.G_NOTETITLE)
            # f = codecs.open(notefile,"w",'utf-8')
            f = open(self.G_NOTEFILE, "w")
            f.write(content)
            f.close()

#############################################################################

    def on_savebutton_clicked(self, widget):
        # Si no hay grupos creados
        if len(self.LStr_grps) == 1:
            errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, "Note Groups")
            errdialog.format_secondary_text("No groups created! \nCreate a note group before saving")
            errdialog.run()
            errdialog.destroy()
        else:
            # If first time, open dialog for info and save
            if self.G_NOTEFILE == "" and self.G_NOTETITLE == "":

                dialog = Gtk.Dialog(title="Creating Note", buttons=(Gtk.STOCK_OK, Gtk.ResponseType.OK, Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
                # dialog.set_default_size(400, 300)

                vboxdiag = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                entrytitle = Gtk.Entry()
                entrytitle.set_text("Title")
                vboxdiag.pack_start(entrytitle, True, True, 0)

                hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
                vboxdiag.pack_start(hbox, True, True, 0)

                label = Gtk.Label("Note Group:", xalign=0)
                combogroup = Gtk.ComboBoxText()

                for i in range(len(self.LStr_grps)):
                    # ith element in list
                    path = Gtk.TreePath(i)
                    treeiter = self.LStr_grps.get_iter(path)
                    if self.LStr_grps.get_value(treeiter, 0) != "Add Group...":
                        # Get value at 1st column
                        combogroup.append_text(self.LStr_grps.get_value(treeiter, 0))

                combogroup.set_active(0)
                hbox.pack_start(label, True, True, 0)
                hbox.pack_start(combogroup, True, True, 0)

                box = dialog.get_content_area()
                box.add(vboxdiag)
                vboxdiag.show_all()

                response = dialog.run()

                if response == Gtk.ResponseType.OK:

                    notetitle = entrytitle.get_text()
                    grp = combogroup.get_active_text()
                    if notetitle == "":
                        errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.OK, "Creating Note")
                        errdialog.format_secondary_text("No title specified!")
                        errdialog.run()
                        errdialog.destroy()
                    else:
                        notefile = ""
                        grptype = ""
                        # Get the group type
                        for i in range(len(self.LStr_grps)):
                            # ith element in list
                            path = Gtk.TreePath(i)
                            treeiter = self.LStr_grps.get_iter(path)
                            # Get value at 1st column
                            grp_ = self.LStr_grps.get_value(treeiter, 0)
                            if grp_ == grp:
                                grptype = self.LStr_grps.get_value(treeiter, 2)
                                break

                        # if grptype == "evernote":
                            #textbuffer = self.noteview.get_buffer()
                            #content=textbuffer.get_text(textbuffer.get_start_iter(),textbuffer.get_end_iter(),False)
                            #notetitle_ = notetitle.replace("'", "")
                            #content_ = content.replace("'", "")
                            ##print "Modified content "+content_
                            #errflag=False
                            #try:

                                #os.system("zenity --progress --pulsate --title 'Connecting to Evernote' &")
                                #socket.setdefaulttimeout(4)
                                #conn = httplib.HTTPConnection('www.evernote.com')  # I used here HTTP not HTTPS for simplify
                                #conn.request('HEAD', '/')  # Just send a HTTP HEAD request
                                #res = conn.getresponse()
                                #os.system("geeknote create --title '"+notetitle_+"' --notebook "+grp+" --content '"+content_+"'")
                                #notif_msg("Saving note "+notetitle+" on Evernote...")

                            #except Exception as e:
                                #print(e)
                                #os.system("killall zenity &")
                                #errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.OK, "Connecting to Evernote")
                                #errdialog.format_secondary_text("Cannot connect to evernote!")
                                #errdialog.run()
                                #errdialog.destroy()
                                #errflag=True

                            ##os.system("gnome-terminal --hide-menubar --command=\"geeknote create --title '"+notetitle+"' --notebook notebox --content '"+content+"'\"")
                            #os.system("killall zenity &")
                            #dialog.destroy()
                            #if not errflag:
                                #Gtk.main_quit()

                        #else:
                        frand = generate_random_string()
                        if grp != "Minutes" and grp != "Private" and grp != "MyNotesGear":
                            notefile = grp + "/" + frand   # Save relative path

                        elif grp == "MyNotesGear" and self.G_MYNOTESGEARFLAG == "1":
                            notetitle = string.replace(notetitle, ' ', '_')
                            notetitle = string.replace(notetitle, '/', '_')
                            notetitle = string.replace(notetitle, '-', '_')
                            notetitle = string.replace(notetitle, ':', '_')
                            currtime = str(int(round(time.time())) * 1000)
                            # currtime= currtime.replace(".","")+"0"
                            notefile = self.G_MYNOTESGEARDIR + "/" + currtime
                            # disable re-save the note
                            self.savebutton.set_sensitive(False)
                        elif grp == "Minutes" and self.G_MINUTESFLAG == "1":
                            notetitle = string.replace(notetitle, ' ', '_')
                            notetitle = string.replace(notetitle, '/', '_')
                            notetitle = string.replace(notetitle, '-', '_')
                            notetitle = string.replace(notetitle, ':', '_')
                            notefile = self.G_MINUTESDIR + "/" + notetitle + ".txt"
                        elif grp == "Private" and self.G_ENCFSFLAG == "1":
                            notetitle = string.replace(notetitle, ' ', '_')
                            notetitle = string.replace(notetitle, '/', '_')
                            notetitle = string.replace(notetitle, '-', '_')
                            notetitle = string.replace(notetitle, ':', '_')
                            notefile = self.G_ENCFSDIR + "/" + notetitle + ".txt"
                        self.G_NOTEFILE = notefile
                        self.G_NOTETITLE = notetitle
                        self.G_NOTEGRP = grp

                        textbuffer = self.noteview.get_buffer()
                        content = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter(), False)
                        # Save the note content######################################################
                        self.__db_savenote(self.G_NOTETITLE, self.G_NOTEGRP, self.G_NOTEFILE, content, "create")

                        # if grp != "Minutes" and grp != "Private" and grp != "MyNotesGear":
                            # #f = codecs.open(BASEDIR+"/"+notefile,"w",'utf-8')
                            # f = open(BASEDIR+"/"+self.G_NOTEFILE,"w")
                            # f.write(content)
                            # f.close()
                            # currtime=int(time.time())
                            # notif_msg("Saving note "+self.G_NOTETITLE)
                            # datfile=open(G_NOTESDAT, 'a')
                            # line=self.G_NOTETITLE+";"+grp+";"+self.G_NOTEFILE+";"+str(currtime)+"\n"
                            # datfile.write(line)
                            # datfile.close()
                        # elif grp == "MyNotesGear":
                            # template_note='{ "note_Id": '+currtime+','+"\n"+' "note_Alarmid": 0,'+"\n"+' "note_Due": 0,'+"\n"+' "note_Lastedit": '+currtime+','+"\n"+' "note_Issynced": false,'+"\n"+' "note_Isedited": true,'+"\n"+' "note_Isdropboxsynced": true,'+"\n"+' "note_Isdropboxedited": true,'+"\n"+' "note_SharedUrl": "",'+"\n"+' "note_Label": "[]",'+"\n"+' "note_Position": 2097151.5,'+"\n"+' "note_Title": "'+self.G_NOTETITLE+'",'+"\n"+' "note_Notes": " '
                            # arraynote=content.split("\n")
                            # for i in arraynote:
                                # template_note=template_note+i+'\n'
                            # template_note= template_note[:-1]+ '",'+"\n"+' "note_Color": "#2196F3",'+"\n"+' "note_Istimeactive": false,'+"\n"+' "note_Islocationactive": false,'+"\n"+' "note_Isarchived": false,'+"\n"+' "note_Isdeleted": false,'+"\n"+' "note_Ischecklist": false,'+"\n"+' "note_Isshared": false,'+"\n"+' "note_Hasfile": false,'+"\n"+' "note_Filepath": "",'+"\n"+' "note_Image": "",'+"\n"+' "note_Address": "",'+"\n"
                            # template_note= template_note+' "note_Longitude": 0,'+"\n"+' "note_Latitude": 0,'+"\n"+' "note_FieldS1": "",'+"\n"+' "note_FieldS2": "",'+"\n"+' "note_FieldL1": 0,'+"\n"+' "note_FieldL2": 0,'+"\n"+' "note_FieldB1": false,'+"\n"+' "note_FieldB2": false'+"\n"+'}'
                            # notif_msg("Saving note "+self.G_NOTETITLE)
                            # f = open(self.G_NOTEFILE,"w")
                            # f.write(template_note)
                            # f.close()
                        # else:
                            # notif_msg("Saving note "+self.G_NOTETITLE)
                            # #f = codecs.open(notefile,"w",'utf-8')
                            # f = open(self.G_NOTEFILE,"w")
                            # f.write(content)
                            # f.close()

                        dialog.destroy()
                elif response == Gtk.ResponseType.CANCEL:
                    print("The Cancel button was clicked")
                    dialog.destroy()
            else:
                textbuffer = self.noteview.get_buffer()
                content = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter(), False)
                # Save the note content######################################################
                self.__db_savenote(self.G_NOTETITLE, self.G_NOTEGRP, self.G_NOTEFILE, content, "save")

##########################################################
    def on_wrapbutton_clicked(self, widget):
        self.noteview.set_wrap_mode(widget.get_active())

##########################################################

    def __db_loadnotegroups(self):

        try:
            output = subprocess.check_output("ls -1d " + BASEDIR + "/* | grep -v dat", shell=True)
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

        if self.G_EVERNOTEFLAG == "1":
            nbs = self.G_EVERNOTENOTEBLIST
            nblist = nbs.split(",")
            for item in nblist:
                newlist.append([item, "evernote", "evernote"])

        for item in tmplist:
            if item != "":
                newlist.append([basename(item), "folder", "folder"])

        if self.G_MYNOTESGEARFLAG == "1":
            newlist.append(["MyNotesGear", "mynotesgearimg", "mynotesgear"])

        if self.G_MINUTESFLAG == "1":
            newlist.append(["Minutes", "minutes", "minutes"])

        if self.G_ENCFSFLAG == "1":
            newlist.append(["Private", "nb_lock", "private"])

        return newlist

# ---------------------------------------------------------------------------------------


note = MyWindow()
# Register app in the notification library
Notify.init("Notebox")
note.connect("delete-event", Gtk.main_quit)
note.show_all()
Gtk.main()
