# -*- coding: utf-8 -*-
"""about_dialog.py - About dialog."""

import webbrowser
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
import pkg_resources

from mcomix import constants
from mcomix import strings
from mcomix import image_tools


class _AboutDialog(Gtk.AboutDialog):

    def __init__(self, window):
        super(_AboutDialog, self).__init__()

        self.set_name(constants.APPNAME)
        self.set_program_name(constants.APPNAME)
        self.set_version(constants.VERSION)
        self.set_website('https://sourceforge.net/p/mcomix/wiki/')
        self.set_copyright('Copyright © 2005-2016')

        icon_data = pkg_resources.resource_string('mcomix.images', 'mcomix.png')
        pixbuf = image_tools.load_pixbuf_data(icon_data)
        self.set_logo(pixbuf)

        comment = \
            ('%s is an image viewer specifically designed to handle comic books.') % \
            constants.APPNAME + u' ' + \
            ('It reads ZIP, RAR and tar archives, as well as plain image files.')
        self.set_comments(comment)

        license = \
            ('%s is licensed under the terms of the GNU General Public License.') % constants.APPNAME + \
            ' ' + \
            ('A copy of this license can be obtained from %s') % \
            'http://www.gnu.org/licenses/gpl-2.0.html'
        self.set_wrap_license(True)
        self.set_license(license)

        authors = [u'%s: %s' % (name, description) for name, description in strings.AUTHORS]
        self.set_authors(authors)

        translators = [u'%s: %s' % (name, description) for name, description in strings.TRANSLATORS]
        self.set_translator_credits("\n".join(translators))

        artists = [u'%s: %s' % (name, description) for name, description in strings.ARTISTS]
        self.set_artists(artists)

        self.show_all()


def open_url(url):
    webbrowser.open(url)


#Gtk.AboutDialog.set_website_label(open_url('https://sourceforge.net/p/mcomix/wiki/'))
# vim: expandtab:sw=4:ts=4
