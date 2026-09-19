from gi.repository import Gtk, Gdk, GLib

from zim.plugins import PluginClass
from zim.gui.pageview import PageViewExtension
from zim.gui.pageview.textbuffer import TextBuffer
from zim.notebook import HRef
from zim.parse.links import link_type


class LinkPreviewPlugin(PluginClass):

    plugin_info = {
        'name': _('Link Preview'),
        'description': _('Show a preview when hovering over a link'),
        'author': 'Nick',
    }


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

        label_text = 'Ссылка: ' + self._hover_link

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
        label.set_line_wrap(True)
        label.set_size_request(600, 150)

        label.set_margin_start(10)
        label.set_margin_end(10)
        label.set_margin_top(7)
        label.set_margin_bottom(7)

        label.set_xalign(0)
        label.set_yalign(0)

        frame.add(label)
        window.add(frame)

        window.show_all()
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
