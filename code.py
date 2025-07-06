import gc
import time

import display
import encoders
import mechs


def main():
    encs = encoders.setup_encoders()
    display.auto_refresh(False)
    labels = display.setup()

    mech_widgets = mechs.load_mechs(encs, labels)

    ms = mechs.MechSwitcher(encs[0], mech_widgets)

    display.refresh()
    last_update = time.monotonic()
    need_gc = False
    while True:
        updated = False
        for enc in encs:
            if enc.update():
                updated = True

        # if need_refresh[0]:
        if updated:
            display.refresh()
            last_update = time.monotonic()
            need_gc = True

        if need_gc:
            since_update = time.monotonic() - last_update
            if since_update > 1:
                print(gc.mem_free())
                gc.collect()
                print(gc.mem_free())
                last_update = time.monotonic()
                need_gc = False


main()
