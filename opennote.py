#!/usr/bin/python
import os
import getopt
import sys
import socket
import httplib
import subprocess
from gi.repository import Gtk, Gio
from gi.repository import Notify

G_MARGIN = 5
HomeDir = os.environ['HOME']
BASEDIR = HomeDir+"/.notebox/notes"
APP = "Notebox"
APPDIR = HomeDir+"/.notebox"
title = ""
filename = ""
group = ""

####################################################


def usage():
    print('Usage opennote.py -t <title> -g <group> -f <note filename>')

####################################################


def notif_msg(app, msg):
    # icon = APPDIR+"/notebox.png"
    # os.system("notify-send -i "+icon+" Notebox \""+msg+"\"")
    n = Notify.Notification.new(app, msg, "")
    n.show()

##################################################


class MyWindow(Gtk.Window):

    def __init__(self, title, grp, fname):
        Gtk.Window.__init__(self, title="")
        # my winIco = Gtk2::Gdk::Pixbuf->new_from_file("$APPDIR/notes.png");
        self.set_icon_from_file(APPDIR+"/notes.png")
        # $window->set_default_icon($winIco);

        # #Spinner window##########################
        # self.win= Gtk.Window()
        # self.win.set_default_size(200, 200)
        # self.spinner = Gtk.Spinner()
        # self.win.connect("delete-event", self.winhide)

        # self.win.add(self.spinner)
        # self.win.hide()
        ##########################################

        # Register app in the notification library
        Notify.init("Notebox")

        self.set_default_size(500, 500)
        self.set_border_width(0)

        self.group = grp
        self.filename = fname
        self.title = title

        # Window content Header bar
        hb = Gtk.HeaderBar()
        hb.set_show_close_button(True)
        hb.props.title = "Note Viewer: "+title
        hb.set_subtitle(grp)

        self.set_titlebar(hb)

        self.newbutton = Gtk.Button()
        self.newbutton.connect("clicked", self.on_newbutton_clicked)
        self.newbutton.set_tooltip_text("New Note")
        icon = Gio.ThemedIcon(name="document-new")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        self.newbutton.add(image)
        hb.pack_start(self.newbutton)

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

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)

        self.noteview = Gtk.TextView()
        # self.noteview.props.margin_top=G_leftm
        # self.noteview.props.margin_left=G_leftm
        # self.noteview.props.margin_right=G_leftm

        self.noteview.set_border_window_size(Gtk.TextWindowType.LEFT, G_MARGIN)
        self.noteview.set_border_window_size(Gtk.TextWindowType.RIGHT, G_MARGIN)
        self.noteview.set_border_window_size(Gtk.TextWindowType.TOP, G_MARGIN)
        self.noteview.set_border_window_size(Gtk.TextWindowType.BOTTOM, G_MARGIN)

        self.noteview.set_wrap_mode(True)
        self.noteview.set_size_request(300, 300)

        content = self.__db_getnotecontent(self.title, self.group, self.filename)
        textbuffer = self.noteview.get_buffer()
        textbuffer.set_text(content)

        scroll.add(self.noteview)

        self.add(scroll)

##############################################

    def on_newbutton_clicked(self, widget):
        os.system("python "+APPDIR+"/addnote.py")

    def on_savebutton_clicked(self, widget):
        textbuffer = self.noteview.get_buffer()
        content = textbuffer.get_text(textbuffer.get_start_iter(), textbuffer.get_end_iter(), False)
        self.__db_savenotecontent(self.title, self.group, self.filename, content)
        ################################################################
        # if self.group != "Minutes" and self.group != "Private":
        #     f = open(BASEDIR+"/"+self.filename,"w",encoding='utf-8')
        # else:
        # f = open(self.filename,"w")
        # f.write(content)
        # f.close()
        ################################################################

    def on_wrapbutton_clicked(self, widget):
        # self.noteview.set_wrap_mode(widget.get_active())
        print ""

#############################################################

    def __db_getnotecontent(self, title, grp, filename):
        content = ""
        if filename != "evernote":
            if grp == "MyNotesGear":
                content = subprocess.check_output("grep note_Notes " + filename+" | cut -d:  -f 2 |  tr -d \\\" | tr -d ,", shell=True)
            elif grp != "Minutes" and grp != "Private" and grp != "Reminders":
                # f = codecs.open( BASEDIR+"/"+filename,"r",'utf-8')
                f = open(BASEDIR+"/"+filename, "r")
                content = f.read()
                f.close()
            else:
                # f = codecs.open(filename,"r",'utf-8')
                f = open(filename, "r")
                content = f.read()
                f.close()
            return content
        else:
            socket.setdefaulttimeout(3)

            try:
                os.system("zenity --progress --pulsate --title 'Connecting to Evernote' &")
                conn = httplib.HTTPConnection('www.evernote.com')  # I used here HTTP not HTTPS for simplify
                conn.request('HEAD', '/')  # Just send a HTTP HEAD request
                res = conn.getresponse()
                content = subprocess.check_output(["geeknote","show",title])
                tmplist = content.split("\n")
                i = 1
                content2 = ""
                for item in tmplist:
                    if i > 5:
                        content2 = item+"\n"+content2
                    i = i+1
                os.system("killall zenity &")
                return content2
            except:
                os.system("killall zenity &")
                errdialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.ERROR,Gtk.ButtonsType.OK, "Error")
                errdialog.format_secondary_text("Error obtaining note content from Evernote!")
                errdialog.run()
                errdialog.destroy()
                Gtk.main_quit()
            return content

#############################################################

    def __db_savenotecontent(self, title, grp, filename, content):
        global APP
        if filename != "evernote":
            if grp == "MyNotesGear":
                # print "Not supported yet!"
                os.system("sed -i 's/\( \"note_Notes\": \"\).*\(\"\)/ \"note_Note\": \""+content+"\"/' "+filename)
                notif_msg(APP, "Note "+title+" Saved!")
                return
            elif grp != "Minutes" and grp != "Private":
                # f = codecs.open(BASEDIR+"/"+filename,"w",'utf-8')
                f = open(BASEDIR+"/"+filename, "w")
            else:
                # f = codecs.open(filename,"w",'utf-8')
                f = open(filename, "w")
            f.write(content)
            f.close()
            notif_msg(APP, "Note "+title+" Saved!")
        else:
            content = content.replace("'", "\'")
            try:
                os.system("geeknote edit --note '"+title+"' --content '"+content+"'")
            except:
                dummy = ""

# ---------------------------------------------------------------------------------------


total = len(sys.argv)

if total < 6:
	usage()
	sys.exit(2)

try:
    opts, args = getopt.getopt(sys.argv[1:], "t:f:g:")
except getopt.GetoptError as err:
    #  print help information and exit:
    print(err)
    usage()
    sys.exit(2)
for o, a in opts:
    if o == "-t":
        title = a
    elif o == "-f":
        filename = a
    elif o == "-g":
        group = a
    else:
        usage()
        sys.exit()

# print "AA "+str(total)+" -- "+filename
# sys.exit()

note = MyWindow(title, group, filename)
note.connect("delete-event", Gtk.main_quit)
note.show_all()
Gtk.main()
