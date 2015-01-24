import sys
import libbtaps
import time


def get_line():
    line = raw_input('> ')
    if line.lower() in ('quit', 'exit', 'kill'):
        exit()
    return line


# Sort day dictionary in Monday-Sunday order
def print_dic_sorted(dic):
    order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    for key in sorted(dic, key=order.index):
        print key, ":", dic[key], "",

    print ""


# Given a list of BTApsTimer objects, print them in a legible format
def print_timers(timer_list):
    print "Timers:"
    for timer in timer_list:
        print "\tName: ", timer.name
        print "\tID: ", timer.timer_id
        print "\tOn: ",
        if timer.on == 1:
            print "On"
        else:
            print "Off"
        print "\tDays: ",
        print_dic_sorted(timer.repeat_days)
        print "\tStart Time: ", timer.start_time
        print "\tEnd Time: ", timer.end_time
        print ""


# Turn switch on/off
def toggle_switch(btaps, status):
    if status == 0:
        btaps.set_switch(True)
    else:
        btaps.set_switch(False)


# Print name and on/off state of switch
def print_status(btaps):
    name = btaps.get_dev_name()
    status = btaps.get_switch_state()

    print "Name: " + name
    print "Switch: ",
    if status[0] == 1:
        print "On"
    else:
        print "Off"

    return status


# Simple interactive command line prompts for creating new timer
def create_timer(btaps, timer_list):
    print "Creating New Timer:"
    print "Name: "
    name = get_line()
    new_timer = libbtaps.BTapsTimer(len(timer_list) + 1, name)

    print "Enter Start and End Time in 24-hour format (ex: 23:54)"
    print "Start Time: "
    start = get_line()
    start = time.strptime(start, "%H:%M")
    new_timer.set_start_time(start[3], start[4])

    print "End Time: "
    end = get_line()
    end = time.strptime(end, "%H:%M")
    new_timer.set_end_time(end[3], end[4])

    print "Repeat Timer?"
    repeat = get_line().lower()
    if repeat == "y":
        day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(day_list):
            print day, "?"
            repeat = get_line().lower()
            if repeat == 'y':
                day_list[i] = True
            else:
                day_list[i] = False

        new_timer.set_repeat_days(day_list[0], day_list[1], day_list[2], day_list[3],
                                  day_list[4], day_list[5], day_list[6])

    print "Enable New Timer? Y/N"
    enable = get_line().lower()
    if enable == 'y':
        new_timer.toggle_on()

    btaps.create_timer(new_timer)


# Simple interactive command line prompts for modifying a timer
def modify_timer(btaps, timer_list):
    print "Enter Timer ID for the timer you wish to modify:"
    id = get_line()
    mod_timer = timer_list[int(id)-1]

    print "Enter values you wish to change, leave blank to keep original value"
    print "Name: ", mod_timer.name
    name = get_line()
    if name != '':
        mod_timer.set_name(name)

    print "Enter Start and End Time in 24-hour format (ex: 23:54)"
    print "Start Time: ",
    print_dic_sorted(mod_timer.start_time)
    start = get_line()
    if start != '':
        start = time.strptime(start, "%H:%M")
        mod_timer.set_start_time(start[3], start[4])

    print "End Time: ", mod_timer.end_time
    end = get_line()
    if end != '':
        end = time.strptime(end, "%H:%M")
        mod_timer.set_end_time(end[3], end[4])

    print "Repeat Timer?", mod_timer.repeat_days
    repeat = get_line().lower()
    if repeat == "y":
        day_list = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        for i, day in enumerate(day_list):
            print day, "?"
            repeat = get_line().lower()
            if repeat == 'y':
                day_list[i] = True
            else:
                day_list[i] = False

        mod_timer.set_repeat_days(day_list[0], day_list[1], day_list[2], day_list[3],
                                  day_list[4], day_list[5], day_list[6])

    print "Enable Timer? Y/N"
    enable = get_line().lower()
    if (enable == 'y') and (mod_timer.on != 1):
        mod_timer.toggle_on()
    elif (enable == 'n') and (mod_timer.on != 0):
        mod_timer.toggle_on()

    btaps.modify_timer(mod_timer)


def main(argv):
    print " === Plugable PS-BTAPS CLI v0.8 ==="
    if len(argv) != 2:
        print "USAGE:   python", sys.argv[0], "[Bluetooth address]"
        print "EXAMPLE: python", sys.argv[0], "00:00:FF:FF:00:00"
        sys.exit(0)

    # Establish connection to BTAPS
    btaps = libbtaps.BTaps(argv[1])
    connected = btaps.connect()
    if not connected:
        sys.exit(0)
    btaps.set_datetime_now()
    status = print_status(btaps)
    print_timers(status[1])

    while True:
        print "Select a function..."
        print "1. (T)oggle Switch"
        print "2. (C)reate Timer"
        print "3. (M)odify Timer"
        print "4. (D)elete Timer"
        print "5. (S)et Device Name"
        print "6. (G)et Switch Status (Name, On/Off, Timers)"
        print "7. E(x)it"

        try:
            function = get_line().lower()
            if function in ['1', 't']:
                toggle_switch(btaps, status[0])
            elif function in ['2', 'c']:
                create_timer(btaps, status[1])
            elif function in ['3', 'm']:
                print_timers(status[1])
                modify_timer(btaps, status[1])
            elif function in ['4', 'd']:
                print_timers(status[1])
                print "Enter Timer ID to delete:"
                timer_id = get_line()
                btaps.delete_timer(timer_id)
            elif function in ['5', 's']:
                print "New Device Name:"
                name = get_line()
                btaps.set_dev_name(name)
            elif function in ['6', 'g']:
                status = print_status(btaps)
                print_timers(status[1])
            elif function in ['7', 'x']:
                break

            if not (function in ['5', 'g']):
                status = print_status(btaps)
        except KeyboardInterrupt:
            break

    btaps.disconnect()

if __name__ == '__main__':
    main(sys.argv)