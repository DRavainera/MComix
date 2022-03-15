"""labels.py - gtk.Label convenience classes."""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

class FormattedLabel(Gtk.Label):

    """FormattedLabel keeps a label always formatted with some pango weight,
    style and scale, even when new text is set using set_text().
    """

    def __init__(self, text='', weight=Pango.AttrType.WEIGHT,
      style=Pango.AttrType.STYLE, scale=Pango.AttrType.SCALE):
        super(FormattedLabel, self).__init__(text)
        self._weight = weight
        self._style = style
        self._scale = scale
        self._format()

    def set_text(self, text):
        Gtk.Label.set_text(self, text)
        self._format()

    def _format(self):
        self.set_markup(str(self._weight))
        self.set_markup(str(self._style))
        self.set_markup(str(self._scale))
        

class BoldLabel(FormattedLabel):

    """A FormattedLabel that is always bold and otherwise normal."""

    def __init__(self, text=''):
        super(BoldLabel, self).__init__(text=text, weight=Pango.Weight.BOLD)

class ItalicLabel(FormattedLabel):

    """A FormattedLabel that is always italic and otherwise normal."""

    def __init__(self, text=''):
        super(ItalicLabel, self).__init__(text=text, style=Pango.Style.ITALIC)


# vim: expandtab:sw=4:ts=4
