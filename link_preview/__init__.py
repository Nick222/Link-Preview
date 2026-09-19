from gi.repository import Gtk, Gdk, GLib

from zim.plugins import PluginClass
from zim.gui.pageview import PageViewExtension


class LinkPreviewPlugin(PluginClass):

    plugin_info = {
        'name': _('Link Preview'),
        'description': _('Show a preview of a link when hovering over it'),
        'author': 'Nick',
    }


class LinkPreviewPageViewExtension(PageViewExtension):

    def __init__(self, pageview):
        super().__init__(pageview)

        self.textview = self.pageview.textview

        self._hover_timeout = None
        self._popup = None
        self._hover_x = 0
        self._hover_y = 0

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

    def _cancel_timeout(self):
        if self._hover_timeout is not None:
            GLib.source_remove(self._hover_timeout)
            self._hover_timeout = None

    def _hide_popup(self):
        self._cancel_timeout()

        if self._popup is not None:
            self._popup.destroy()
            self._popup = None

    def _on_leave(self, textview, event):
        self._cancel_timeout()
        return False

    def _on_motion(self, textview, event):
        self._hover_x = event.x
        self._hover_y = event.y

        self._cancel_timeout()

        self._hover_timeout = GLib.timeout_add(
            500,
            self._show_preview
        )

        return False

    def _show_preview(self):
        self._hover_timeout = None

        x = int(self._hover_x)
        y = int(self._hover_y)

        text_iter = self.textview.get_iter_at_location(
            x,
            y
        )

        tags = text_iter.get_tags()

        link_tag = None

        for tag in tags:
            name = tag.get_property('name')

            if name and 'link' in name.lower():
                link_tag = tag
                break

        if link_tag is None:
            return False

        self._show_popup(
            'Ссылка обнаружена'
        )

        return False

    def _show_popup(self, text):
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

        label = Gtk.Label(
            label=text
        )

        label.set_margin_start(10)
        label.set_margin_end(10)
        label.set_margin_top(7)
        label.set_margin_bottom(7)

        frame.add(label)
        window.add(frame)

        window.show_all()

        toplevel = self.pageview.get_toplevel()

        window.set_transient_for(
            toplevel
        )

        allocation = self.textview.get_allocation()

        root_x, root_y = self.textview.translate_coordinates(
            toplevel,
            0,
            0
        )

        window.move(
            root_x + int(self._hover_x) + 15,
            root_y + int(self._hover_y) + 20
        )

        self._popup = window

        return False
