Using libbtaps.py
=================

**Establishing Connection, getting device name, then disconnecting**

You can either use the with syntax, or simply call connect/disconnect.

Example 1:
::

    import btaps.libbtaps as libbtaps

    # Bluetooth Device Address for your PS-BTAPS1
    bdaddr = "00:00:00:00:00:00"

    with libbtaps.BTaps(bdaddr) as btapsobj:
        name = btapsobj.get_dev_name()

    print name

Example 2:
::

    import btaps.libbtaps as libbtaps

    # Bluetooth Device Address for your PS-BTAPS1
    bdaddr = "00:00:00:00:00:00"

    btapsobj = libbtaps.BTaps(bdaddr)
    btapsobj.connect()
    name = btapsobj.get_dev_name()
    btapsobj.disconnect()
    print name

**Turning Switch ON/OFF**
::

    import btaps.libbtaps as libbtaps

    with libbtaps.BTaps("00:00:00:00:00:00") as btapsobj:
        # ON
        btapsobj.set_switch(True)

        # OFF
        btapsobj.set_switch(False)

**Creating a timer**
::

    import btaps.libbtaps as libbtaps

    # Create a timer object with ID 1 and named Example Timer
    timerobj = libbtaps.BTapsTimer(1, "Example Timer")

    # Set timer to repeat on Mondays
    timerobj.set_repeat_days(mon = True)

    # Set timer to start at 10AM
    timerobj.set_start_time(10, 0)

    # Set timer to end at 4PM
    timerobj.set_end_time(16, 0)

    # New timers default to OFF, toggle timer ON
    timerobj.toggle_on()

    with libbtaps.BTaps("00:00:00:00:00:00") as btapsobj:
        # Send timer information to device and create new timer
        btapsobj.create_timer(timerobj)

**Modifying existing timer**
::

    import btaps.libbtaps as libbtaps

    with libbtaps.BTaps("00:00:00:00:00:00") as btapsobj:
        # Get saved timers and on/off information
        on, timer_list = btapsobj.get_switch_state()

        # timer_list is a list of all timers in device. Here we are just selecting the first timer on the list
        mod_timer = timer_list[0]

        # Stop timer from repeating on Mondays, set it to repeat on Tuesdays
        mod_timer.set_repeat_days(mon = False, tue = True)

        # Send modified timer back to device
        btapsobj.modify_timer(mod_timer)

**More Examples**

For more usage examples, please look at btaps.py.