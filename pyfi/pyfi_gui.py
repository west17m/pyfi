import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='FileMenu'>
      <menuitem action='FileOpen' />
      <menuitem action='FileQuit' />
    </menu>
  </menubar>
</ui>
"""

class MenuExampleWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="PyFi")

        self.set_default_size(800, 600)

        action_group = Gtk.ActionGroup("my_actions")

        self.add_file_menu_actions(action_group)

        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/MenuBar")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)

        self.add(box)

    def add_file_menu_actions(self, action_group):
        action_filemenu = Gtk.Action("FileMenu", "File", None, None)
        action_group.add_action(action_filemenu)

        action_fileopen = Gtk.Action("FileOpen", None, None, Gtk.STOCK_OPEN)
        action_filequit = Gtk.Action("FileQuit", None, None, Gtk.STOCK_QUIT)

        action_fileopen.connect("activate", self.on_menu_file_open)
        action_filequit.connect("activate", self.on_menu_file_quit)

        action_group.add_action(action_fileopen)
        action_group.add_action(action_filequit)

    def create_ui_manager(self):
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(UI_INFO)

        return uimanager

    def on_menu_file_quit(self, widget):
        Gtk.main_quit()

    def on_menu_file_open(self, widget):
        print "open file"
        Gtk.main_quit()

window = MenuExampleWindow()
window.connect("delete-event", Gtk.main_quit)
window.show_all()
Gtk.main()
