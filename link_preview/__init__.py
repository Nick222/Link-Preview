from gi.repository import Gtk, Gdk, GLib

from zim.plugins import PluginClass
from zim.gui.pageview import PageViewExtension
from zim.gui.pageview.textbuffer import TextBuffer
from zim.notebook import HRef, get_notebook_list
from zim.parse.links import link_type


class LinkPreviewPlugin(PluginClass):

    plugin_info = {
        'name': _('Link Preview'),
        'description': _('Show a preview when hovering over a link'),
        'author': 'Nick',
    }

    plugin_preferences = (
        (
            'preview_start_line',
            'int',
            'First non-empty preview line',
            1,
            (1, 1000),
        ),
        (
            'preview_line_count',
            'int',
            'Number of preview lines',
            5,
            (1, 100),
        ),
        (
            'max_line_chars',
            'int',
            'Maximum characters per line',
            100,
            (1, 1000),
        ),
    )


class LinkPreviewPageViewExtension(PageViewExtension):

    def __init__(self, plugin, pageview):
        super().__init__(plugin, pageview)

        print("LINK PREVIEW: extension created")

        self.textview = self.pageview.textview

        self._hover_timeout = None
        self._popup = None
        self._hover_x = 0
        self._hover_y = 0
        self._hover_link = None

        self.textview.add_events(
            Gdk.EventMask.POINTER_MOTION_MASK |
            Gdk.EventMask.LEAVE_NOTIFY_MASK
        )

        self.textview.connect(
            'motion-notify-event',
            self._on_motion
        )

        self.textview.connect(
            'leave-notify-event',
            self._on_leave
        )

    def _on_motion(self, textview, event):
        iter, coords = self.textview._get_pointer_location()

        link = None

        if iter:
            link = self.textview.get_buffer().get_link_data(iter)

        self._hover_x = event.x
        self._hover_y = event.y

        self._cancel_timeout()

        if link:
            self._hover_link = link['href']

            print(
                "LINK PREVIEW: link =",
                link
            )

            self._hover_timeout = GLib.timeout_add(
                500,
                self._show_preview
            )
        else:
            self._hover_link = None
            self._hide_popup()

        return False

    def _on_leave(self, textview, event):
        self._cancel_timeout()
        self._hide_popup()
        self._hover_link = None

        return False

    def _cancel_timeout(self):
        if self._hover_timeout is not None:
            GLib.source_remove(
                self._hover_timeout
            )
            self._hover_timeout = None

    def _show_preview(self):
        self._hover_timeout = None

        if self._hover_link:
            self._show_popup()

        return False

    def _hide_popup(self):
        if self._popup is not None:
            self._popup.destroy()
            self._popup = None

    def _show_popup(self):
        self._hide_popup()

        window = Gtk.Window(
            type=Gtk.WindowType.POPUP
        )

        window.set_decorated(False)
        window.set_resizable(False)

        frame = Gtk.Frame()

        frame.set_shadow_type(
            Gtk.ShadowType.OUT
        )

        href = self._hover_link

        print(
            'LINK PREVIEW: href =',
            href
        )

        print(
            'LINK PREVIEW: link_type =',
            link_type(href)
        )

        if href.startswith(('http://', 'https://')):
            label_text = 'Интернет-ссылка'

        elif href.startswith('zotero://'):
            label_text = 'Zotero-ссылка'

        elif link_type(href) == 'interwiki':
            interwiki = href.split('?', 1)[0]
            notebook_name = interwiki

            for notebook in get_notebook_list():
                if notebook.interwiki == interwiki:
                    notebook_name = notebook.name
                    break

            label_text = 'Ссылка на блокнот ' + notebook_name

        else:
            label_text = 'Ссылка: ' + href

        if link_type(self._hover_link) == 'page':
            href_obj = HRef.new_from_wiki_link(
                self._hover_link
            )

            path = self.pageview.notebook.pages.resolve_link(
                self.pageview.page,
                href_obj
            )

            print(
                "LINK PREVIEW: path =",
                path
            )

            page = self.pageview.notebook.get_page(path)
            tree = page.get_parsetree()

            print("LINK PREVIEW: page =", page)
            print("LINK PREVIEW: hascontent =", page.hascontent)
            print("LINK PREVIEW: tree =", tree)
            print("LINK PREVIEW: tree.hascontent =", tree.hascontent if tree else None)

            if tree is not None:
                buffer = TextBuffer(
                    self.pageview.notebook,
                    page,
                    parsetree=tree
                )

                print(
                    "LINK PREVIEW: buffer hascontent =",
                    buffer.hascontent
                )

                start = buffer.get_start_iter()
                end = buffer.get_end_iter()

                label_text = buffer.get_text(
                    start,
                    end,
                    True
                )

                lines = label_text.splitlines()

                nonempty_lines = [
                    line for line in lines
                    if line.strip()
                ]

                preview_start_line = self.plugin.preferences[
                    'preview_start_line'
                ]

                preview_line_count = self.plugin.preferences[
                    'preview_line_count'
                ]

                max_line_chars = self.plugin.preferences[
                    'max_line_chars'
                ]

                preview_lines = nonempty_lines[
                    preview_start_line - 1:
                    preview_start_line - 1 + preview_line_count
                ]

                preview_lines = [
                    line[:max_line_chars] + '...'
                    if len(line) > max_line_chars
                    else line
                    for line in preview_lines
                ]

                print(
                    "LINK PREVIEW: preview lines =",
                    repr(preview_lines)
                )

                label_text = '\n'.join(preview_lines)

                print(
                    "LINK PREVIEW: text length =",
                    len(label_text)
                )
                print(
                    "LINK PREVIEW: text =",
                    repr(label_text[:500])
                )

        label = Gtk.Label()
        label.set_text(label_text)
        print(
            "LINK PREVIEW: label text =",
            repr(label.get_text())
        )
        label.set_line_wrap(False)

        label.set_margin_start(10)
        label.set_margin_end(10)
        label.set_margin_top(7)
        label.set_margin_bottom(7)

        label.set_xalign(0)
        label.set_yalign(0)

        frame.add(label)
        window.add(frame)

        window.show_all()
        print(
            "LINK PREVIEW: label size =",
            label.get_allocated_width(),
            label.get_allocated_height()
        )
        self.pageview._overlay_label.hide()
        window.realize()

        display = self.textview.get_display()
        seat = display.get_default_seat()
        pointer = seat.get_pointer()

        screen, pointer_x, pointer_y = pointer.get_position()

        print(
            "LINK PREVIEW: popup size =",
            window.get_size()
        )
        print(
            "LINK PREVIEW: popup position =",
            pointer_x + 15,
            pointer_y + 15
        )

        window.move(
            pointer_x + 15,
            pointer_y + 15
        )

        self._popup = window
