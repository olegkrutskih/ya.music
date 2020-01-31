#!/usr/bin/env python3
import gi
gi.require_version("Gtk", "3.0")
gi.require_version('WebKit2', '4.0')
import os, sys

from gi.repository import GLib, Gtk, Gio, WebKit2
import pyxhook


class Browser:

    def __init__(self):
        self.window = Gtk.Window()

        self.window.set_icon_from_file(get_resource_path("icon.png"))

        self.window.set_size_request(1000, 600)
        self.window.set_default_size(800, 600)
        self.s = Gtk.ScrolledWindow()
        self.context = WebKit2.WebContext.get_default()
        sm = self.context.get_security_manager()
        self.cookies = self.context.get_cookie_manager()
        self.manager = WebKit2.UserContentManager()

        self.view = WebKit2.WebView.new_with_user_content_manager(self.manager)
        self.settings = self.view.get_settings()

        cookies_path = '/tmp/cookies.txt'
        storage = WebKit2.CookiePersistentStorage.TEXT
        policy = WebKit2.CookieAcceptPolicy.ALWAYS
        self.cookies.set_accept_policy(policy)
        self.cookies.set_persistent_storage(cookies_path, storage)

        self.view.load_uri("https://music.yandex.ru/")
        self.s.add(self.view)

        self.hb = Gtk.HeaderBar()
        self.hb.set_show_close_button(True)
        self.window.set_titlebar(self.hb)

        button = Gtk.Button()
        icon = Gio.ThemedIcon(name="mail-send-receive-symbolic")
        image = Gtk.Image.new_from_gicon(icon, Gtk.IconSize.BUTTON)
        button.add(image)
        button.connect("clicked", self.on_refresh)
        self.hb.pack_end(button)

        box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        Gtk.StyleContext.add_class(box.get_style_context(), "linked")

        button1 = Gtk.Button()
        button1.add(Gtk.Arrow(Gtk.ArrowType.LEFT, Gtk.ShadowType.NONE))
        button1.connect("clicked", self.on_back)
        box.add(button1)

        self.button_play = Gtk.Button.new_with_label("Play/Pause")
        self.button_play.connect("clicked", self.on_play)
        box.add(self.button_play)

        button2 = Gtk.Button()
        button2.add(Gtk.Arrow(Gtk.ArrowType.RIGHT, Gtk.ShadowType.NONE))
        button2.connect("clicked", self.on_next)
        box.add(button2)

        self.hb.pack_start(box)

        self.window.add(self.s)

        self.window.show_all()
        self.window.connect('destroy', self.destroy)

    def destroy(self, w):
        # self.hookman.cancel()
        Gtk.main_quit()

    def on_refresh(self, button):
        self.refresh()

    def refresh(self):
        self.view.load_uri("https://music.yandex.ru")
        return False

    def on_back(self, button):
        self.do_back()

    def do_back(self):
        self.view.run_javascript('externalAPI.prev();')

    def on_next(self, button):
        self.do_next()

    def do_next(self):
        self.view.run_javascript('externalAPI.next();')

    def on_play(self, button):
        self.play()

    def play(self):
        self.view.run_javascript('externalAPI.togglePause();')


class App:
    def __init__(self):
        self.browser = Browser()
        self.hookman = pyxhook.HookManager()
        self.hookman.KeyUp = self.kbevent
        self.hookman.HookKeyboard()
        self.hookman.start()

    def kbevent(self, event):
        global running
        # print(event) <- тут можно отловить нужные сканкоды и назначить на любые клавиши ниже
        if event.ScanCode == 172:
            GLib.idle_add(self.browser.play)
        if event.ScanCode == 166:
            GLib.idle_add(self.browser.do_back)
        if event.ScanCode == 167:
            GLib.idle_add(self.browser.do_next)


def get_resource_path(rel_path):
    dir_of_py_file = os.path.dirname(__file__)
    rel_path_to_resource = os.path.join(dir_of_py_file, rel_path)
    abs_path_to_resource = os.path.abspath(rel_path_to_resource)
    return abs_path_to_resource


def main():
    app = App()
    Gtk.main()


if __name__ == "__main__":
    main()
