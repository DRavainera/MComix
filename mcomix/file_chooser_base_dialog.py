"""filechooser_chooser_base_dialog.py - Custom FileChooserDialog implementations."""

import os
import mimetypes
import fnmatch
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango, Gdk

from mcomix.preferences import prefs
from mcomix import image_tools
from mcomix import archive_tools
from mcomix import labels
from mcomix import constants
from mcomix import log
from mcomix import thumbnail_tools
from mcomix import message_dialog
from mcomix import file_provider
from mcomix import tools

mimetypes.init()

class _BaseFileChooserDialog(Gtk.Dialog):

    """We roll our own FileChooserDialog because the one in GTK seems
    buggy with the preview widget. The <action> argument dictates what type
    of filechooser dialog we want (i.e. it is gtk.FILE_CHOOSER_ACTION_OPEN
    or gtk.FILE_CHOOSER_ACTION_SAVE).

    This is a base class for the _MainFileChooserDialog, the
    _LibraryFileChooserDialog and the SimpleFileChooserDialog.

    Subclasses should implement a method files_chosen(paths) that will be
    called once the filechooser has done its job and selected some files.
    If the dialog was closed or Cancel was pressed, <paths> is the empty list.
    """

    _last_activated_file = None

    def __init__(self, action=Gtk.FileChooserAction.OPEN):
        self._action = action
        self._destroyed = False

        if action == Gtk.FileChooserAction.OPEN:
            title = ('Open')
            buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_OPEN, Gtk.ResponseType.OK)

        else:
            title = ('Save')
            buttons = (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                Gtk.STOCK_SAVE, Gtk.ResponseType.OK)

        super(_BaseFileChooserDialog, self).__init__(title, None, 0, buttons)
        self.set_default_response(Gtk.ResponseType.OK)

        self.filechooser = Gtk.FileChooserWidget(action=action)
        self.filechooser.set_size_request(680, 420)
        self.vbox.pack_start(self.filechooser, True, True, 10)
        self.set_border_width(4)
        self.filechooser.set_border_width(6)
        self.connect('response', self._response)
        self.filechooser.connect('file_activated', self._response,
            Gtk.ResponseType.OK)

        preview_box = Gtk.VBox(False, 10)
        preview_box.set_size_request(130, 0)
        self._preview_image = Gtk.Image()
        self._preview_image.set_size_request(130, 130)
        preview_box.pack_start(self._preview_image, False, False, 10)
        self.filechooser.set_preview_widget(preview_box)

        pango_scale_small = (1 / 1.2)

        self._namelabel = labels.FormattedLabel(weight=Pango.Weight.BOLD,
            scale=pango_scale_small)
        self._namelabel.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        preview_box.pack_start(self._namelabel, False, False, 10)

        self._sizelabel = labels.FormattedLabel(scale=pango_scale_small)
        self._sizelabel.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        preview_box.pack_start(self._sizelabel, False, False, 10)
        self.filechooser.set_use_preview_label(False)
        preview_box.show_all()
        self.filechooser.connect('update-preview', self._update_preview)

        self._all_files_filter = self.add_filter( ('All files'), [], ['*'])
        ex = ""
        try:
            current_file = self._current_file()
            last_file = self.__class__._last_activated_file

            # If a file is currently open, use its path
            if current_file and os.path.exists(current_file):
                self.filechooser.set_current_folder(os.path.dirname(current_file))
            # If no file is open, use the last stored file
            elif (last_file and os.path.exists(last_file)):
                self.filechooser.set_filename(last_file)
            # If no file was stored yet, fall back to preferences
            elif os.path.isdir(prefs['path of last browsed in filechooser']):
                if prefs['store recent file info']:
                    self.filechooser.set_current_folder(
                        prefs['path of last browsed in filechooser'])
                else:
                    self.filechooser.set_current_folder(
                        constants.HOME_DIR)

        except Exception(ex): # E.g. broken prefs values.
            log.debug(ex)

        self.show_all()

    def add_filter(self, name, mimes, patterns=[]):
        """Add a filter, called <name>, for each mime type in <mimes> and
        each pattern in <patterns> to the filechooser.
        """
        ffilter = Gtk.FileFilter()
        ffilter.add_custom(
                Gtk.FileFilterFlags.FILENAME|Gtk.FileFilterFlags.MIME_TYPE,
                self._filter, (patterns, mimes))

        ffilter.set_name(name)
        self.filechooser.add_filter(ffilter)
        return ffilter

    def add_archive_filters(self):
        """Add archive filters to the filechooser.
        """
        ffilter = Gtk.FileFilter()
        ffilter.set_name(('All archives'))
        self.filechooser.add_filter(ffilter)
        supported_formats = archive_tools.get_supported_formats()
        for name in sorted(supported_formats):
            mime_types, extensions = supported_formats[name]
            patterns = ['*.%s' % ext for ext in extensions]
            self.add_filter(('%s archives') % name, mime_types, patterns)
            for mime in mime_types:
                ffilter.add_mime_type(mime)
            for pat in patterns:
                ffilter.add_pattern(pat)

    def add_image_filters(self):
        """Add images filters to the filechooser.
        """
        ffilter = Gtk.FileFilter()
        ffilter.set_name(('All images'))
        self.filechooser.add_filter(ffilter)
        supported_formats = image_tools.get_supported_formats()
        for name in sorted(supported_formats):
            mime_types, extensions = supported_formats[name]
            patterns = ['*.%s' % ext for ext in extensions]
            self.add_filter(('%s images') % name, mime_types, patterns)
            for mime in mime_types:
                ffilter.add_mime_type(mime)
            for pat in patterns:
                ffilter.add_pattern(pat)

    def _filter(self, filter_info, data):
        """ Callback function used to determine if a file
        should be filtered or not. C{data} is a tuple containing
        (patterns, mimes) that should pass the test. Returns True
        if the file passed in C{filter_info} should be displayed. """

        path = filter_info
        uri = filter_info
        display = filter_info
        mime = filter_info
        match_patterns, match_mimes = data

        matches_mime = bool(filter(
            lambda match_mime: match_mime == mime,
            match_mimes))
        matches_pattern = bool(filter(
            lambda match_pattern: fnmatch.fnmatch(path, match_pattern),
            match_patterns))

        return matches_mime or matches_pattern

    def collect_files_from_subdir(self, path, filter, recursive=False):
        """ Finds archives within C{path} that match the
        L{gtk.FileFilter} passed in C{filter}. """

        for root, dirs, files in os.walk(path):
            for file in files:
                full_path = os.path.join(root, file)
                mimetype = mimetypes.guess_type(full_path)[0] or 'application/octet-stream'

                if (filter == self._all_files_filter or
                    filter.filter((full_path.encode('utf-8'),
                    None, None, mimetype))):

                    yield full_path

            if not recursive:
                break

    def set_save_name(self, name):
        self.filechooser.set_current_name(name)

    def set_current_directory(self, path):
        self.filechooser.set_current_folder(path)

    def should_open_recursive(self):
        return False

    def _response(self, widget, response):
        """Return a list of the paths of the chosen files, or None if the
        event only changed the current directory.
        """
        if response == Gtk.ResponseType.OK:
            if not self.filechooser.get_filenames():
                return

            # Collect files, if necessary also from subdirectories
            filter = self.filechooser.get_filter()
            paths = [ ]
            for path in self.filechooser.get_filenames():
                path = path.decode('utf-8')

                if os.path.isdir(path):
                    subdir_files = list(self.collect_files_from_subdir(path, filter,
                        self.should_open_recursive()))
                    file_provider.FileProvider.sort_files(subdir_files)
                    paths.extend(subdir_files)
                else:
                    paths.append(path)

            # FileChooser.set_do_overwrite_confirmation() doesn't seem to
            # work on our custom dialog, so we use a simple alternative.
            first_path = self.filechooser.get_filenames()[0].decode('utf-8')
            if (self._action == Gtk.FileChooserAction.SAVE and
                not os.path.isdir(first_path) and
                os.path.exists(first_path)):

                overwrite_dialog = message_dialog.MessageDialog(None, 0,
                    Gtk.MessageType.QUESTION, Gtk.ButtonsType.OK_CANCEL)
                overwrite_dialog.set_text(
                    ("A file named '%s' already exists. Do you want to replace it?") %
                        os.path.basename(first_path),
                    ('Replacing it will overwrite its contents.'))
                response = overwrite_dialog.run()

                if response != Gtk.ResponseType.OK:
                    self.emit_stop_by_name('response')
                    return

            # Do not store path if the user chose not to keep a file history
            if prefs['store recent file info']:
                prefs['path of last browsed in filechooser'] = \
                    self.filechooser.get_current_folder()
            else:
                prefs['path of last browsed in filechooser'] = \
                    constants.HOME_DIR

            self.__class__._last_activated_file = first_path
            self.files_chosen(paths)

        else:
            self.files_chosen([])

        self._destroyed = True

    def _update_preview(self, *args):
        if self.filechooser.get_preview_filename():
            path = Gdk.utf8_to_string_target(self.filechooser.get_preview_filename())
        else:
            path = None

        if path and os.path.isfile(path):
            thumbnailer = thumbnail_tools.Thumbnailer(size=(128, 128),
                                                      archive_support=True)
            thumbnailer.thumbnail_finished += self._preview_thumbnail_finished
            thumbnailer.thumbnail(path)
        else:
            self._preview_image.clear()
            self._namelabel.set_text('')
            self._sizelabel.set_text('')

    def _preview_thumbnail_finished(self, filepath, pixbuf):
        """ Called when the thumbnailer has finished creating
        the thumbnail for <filepath>. """

        if self._destroyed:
            return

        current_path = self.filechooser.get_preview_filename()
        if current_path and current_path.decode('utf-8') == filepath:

            if pixbuf is None:
                self._preview_image.clear()
                self._namelabel.set_text('')
                self._sizelabel.set_text('')

            else:
                pixbuf = image_tools.add_border(pixbuf, 1)
                self._preview_image.set_from_pixbuf(pixbuf)
                self._namelabel.set_text(os.path.basename(filepath))
                self._sizelabel.set_text(tools.format_byte_size(
                    os.stat(filepath).st_size))

    def _current_file(self):
        # XXX: This method defers the import of main to avoid cyclic imports
        # during startup.

        from mcomix import main
        return main.main_window().filehandler.get_path_to_base()

# vim: expandtab:sw=4:ts=4