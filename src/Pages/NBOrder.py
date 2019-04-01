import gi

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk


class NBOrder:
    def __init__(self, gui_base, infocollector):
        self.gui_base = gui_base
        self.infocollector = infocollector
        self.page = None
        self.status_entry = None
        self.add_order_notes = None
        self.infocollector.debug_info("Information", "Order - Variables Initialized")

    def create_page(self):
        self.page = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        wrapper = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        columns = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        column_box1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0, homogeneous=True)
        column_box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)

        order_name_box = Gtk.Box(homogeneous=True)
        order_name_label = self.gui_base.create_label("Order Title:")
        order_name_entry = self.gui_base.create_entry(self.infocollector.order_Name, False)
        order_name_box.pack_start(order_name_label, True, True, 0)
        order_name_box.pack_start(order_name_entry, True, True, 0)
        column_box1.pack_start(order_name_box, True, True, 0)

        client_name_box = Gtk.Box(homogeneous=True)
        client_name_label = self.gui_base.create_label("Order Client:")
        client_name_entry = self.gui_base.create_entry(self.infocollector.order_Client, False)
        client_name_box.pack_start(client_name_label, True, True, 0)
        client_name_box.pack_start(client_name_entry, True, True, 0)
        column_box1.pack_start(client_name_box, True, True, 0)

        current_status_box = Gtk.Box(homogeneous=True)
        current_status_label = self.gui_base.create_label("Current Status:")
        current_status_entry = self.gui_base.create_entry(self.infocollector.order_Status, False)
        current_status_box.pack_start(current_status_label, True, True, 0)
        current_status_box.pack_start(current_status_entry, True, True, 0)
        column_box1.pack_start(current_status_box, True, True, 0)

        box1, status_label, self.status_entry = self.gui_base.create_label_dropbox("New Status",
                                                                                   self.infocollector.order_AvailStatus)
        box1.pack_start(status_label, True, True, 0)
        box1.pack_start(self.status_entry, True, True, 0)
        column_box1.pack_start(box1, True, True, 0)

        add_notes_label = self.gui_base.create_label("\nAdditional Notes:")
        self.add_order_notes = self.gui_base.create_multiline_entry()
        self.add_order_notes.get_children()[0].set_editable(False)
        column_box2.pack_start(add_notes_label, False, True, 0)
        column_box2.pack_start(self.add_order_notes, True, True, 0)

        columns.pack_start(column_box1, False, False, 0)
        columns.pack_start(column_box2, True, True, 0)
        wrapper.pack_start(columns, True, True, 0)

        self.page.pack_start(wrapper, True, True, 0)
