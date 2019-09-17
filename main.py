
if __name__ == '__main__':
    import sys
    import pyglet
    from pyglet import gl
    import imgui

    from imgui.integrations.pyglet import PygletRenderer

    win = pyglet.window.Window(fullscreen=True)
    gl.glClearColor(1, 1, 1, 1)
    imgui.create_context()
    impl = PygletRenderer(win)

    def update(dt):
        imgui.new_frame()
        imgui.show_test_window()

    @win.event
    def on_draw():
        win.clear()
        imgui.render()
        impl.render(imgui.get_draw_data())

    def on_key_press(symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE:
            impl.shutdown()
            sys.exit(0)

    win.event(on_key_press)

    while True:
        pyglet.clock.tick()
        win.switch_to()
        win.dispatch_events()
        update(1/60)
        win.dispatch_event('on_draw')
        win.flip()
