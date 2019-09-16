
if __name__ == '__main__':
    import pyglet
    from pyglet import gl
    import imgui

    from imgui.integrations.pyglet import PygletRenderer

    win = pyglet.window.Window(fullscreen=True)
    gl.glClearColor(1, 1, 1, 1)
    imgui.create_context()
    impl = PygletRenderer(win)

    @win.event
    def on_draw():
        win.clear()
        imgui.new_frame()
        imgui.show_test_window()
        imgui.render()
        impl.render(imgui.get_draw_data())

    pyglet.app.run()
    impl.shutdown()
