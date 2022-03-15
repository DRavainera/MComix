"""properties_page.py - A page to put in the properties dialog window."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from mcomix import i18n
from mcomix import image_tools
from mcomix import labels

class _Page(Gtk.ScrolledWindow):

    """A page to put in the gtk.Notebook. Contains info about a file (an
    image or an archive.)
    """

    def __init__(self):
        super(_Page, self).__init__()
        self.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self._vbox = Gtk.VBox(False, 12)
        self.add_with_viewport(self._vbox)

        self.set_border_width(12)
        topbox = Gtk.HBox(False, 12)
        self._vbox.pack_start(topbox)
        self._thumb = Gtk.Image()
        self._thumb.set_size_request(128, 128)
        topbox.pack_start(self._thumb, False, False)
        borderbox = Gtk.Frame()
        borderbox.set_shadow_type(Gtk.ShadowType.ETCHED_IN)
        borderbox.set_size_request(-1, 130)
        topbox.pack_start(borderbox)
        insidebox = Gtk.EventBox()
        insidebox.set_border_width(1)
        insidebox.set_state(Gtk.StateType.ACTIVE)
        borderbox.add(insidebox)
        self._insidebox = insidebox
        self._mainbox = None
        self._extrabox = None
        self.reset()

    def reset(self):
        self._thumb.clear()
        if self._mainbox is not None:
            self._mainbox.destroy()
        self._mainbox = Gtk.VBox(False, 5)
        self._mainbox.set_border_width(10)
        self._insidebox.add(self._mainbox)
        if self._extrabox is not None:
            self._extrabox.destroy()
        self._extrabox = Gtk.HBox(False, 10)
        self._vbox.pack_start(self._extrabox, False, False)

    def set_thumbnail(self, pixbuf):
        pixbuf = image_tools.add_border(pixbuf, 1)
        self._thumb.set_from_pixbuf(pixbuf)

    def set_filename(self, filename):
        """Set the filename to be displayed to <filename>. Call this before
        set_main_info().
        """
        label = labels.BoldLabel(i18n.to_unicode(filename))
        label.set_alignment(0, 0.5)
        label.set_selectable(True)
        self._mainbox.pack_start(label, False, False)
        self._mainbox.pack_start(Gtk.VBox()) # Just to add space (better way?)

    def set_main_info(self, info):
        """Set the information in the main info box (below the filename) to
        the values in the sequence <info>.
        """
        for text in info:
            label = Gtk.Label(text)
            label.set_alignment(0, 0.5)
            label.set_selectable(True)
            self._mainbox.pack_start(label, False, False)

    def set_secondary_info(self, info):
        """Set the information below the main info box to the values in the
        sequence <info>. Each entry in info should be a tuple (desc, value).
        """
        left_box = Gtk.VBox(True, 8)
        right_box = Gtk.VBox(True, 8)
        self._extrabox.pack_start(left_box, False, False)
        self._extrabox.pack_start(right_box, False, False)
        for desc, value in info:
            desc_label = labels.BoldLabel('%s:' % desc)
            desc_label.set_alignment(1.0, 1.0)
            left_box.pack_start(desc_label, True, True)
            value_label = Gtk.Label(value)
            value_label.set_alignment(0, 1.0)
            value_label.set_selectable(True)
            right_box.pack_start(value_label, True, True)

# vim: expandtab:sw=4:ts=4
