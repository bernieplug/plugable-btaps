from array import array
import sys
import datetime

if sys.platform.startswith('darwin'):
    sys.exit(1)
    #import lightblue-shim as bluetooth
else:
    import bluetooth


# Converts badly formatted hex into decimal values.
# Example: 0x20 becomes 20
def bad_hex_to_dec(hexa):
    return (int(hexa/16) * 10) + hexa % 16


# Main BTAPS control class, represents one connection to a BTAPS device
class BTaps:
    # btaddr = (str) The Bluetooth Hardware address of your BTAPS unit
    def __init__(self, btaddr):
        self.socket = None
        self.btaddr = btaddr

    # For use with the with statement
    def __enter__(self):
        self.connect()
        return self

    # For use with the with statement
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    def __recv_data(self, length=128):
        try:
            data = self.socket.recv(length)
            return data
        except IOError as e:
            print e
            pass

    # Find and connect to btaddr provided when instantiating class
    def connect(self):
        matches = bluetooth.find_service(address=self.btaddr)

        if len(matches) == 0:
            return 0

        for match in matches:
            if match['protocol'] == 'RFCOMM' and bluetooth.SERIAL_PORT_PROFILE in match['profiles']:
                device = match
                break
        else:
            return 0

        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        try:
            self.socket.connect((device["host"], device["port"]))
        except bluetooth.btcommon.BluetoothError:
            return 0
        return 1

    # Disconnect from BTAPS device, closing the socket
    def disconnect(self):
        if self.socket:
            self.socket.close()

    # Send packet containing current date and time. Usually sent once after connection with device.
    def set_datetime_now(self):
        now = datetime.datetime.now()
        # Set Date/Time Packet: 0xCCAA090901(year)(month)(day)(hour)(minute)(second)(weekday number)
        payload = buffer(array('B', [0xcc, 0xaa, 0x09, 0x09, 0x01,
                                     int(now.strftime('%y'), 16), int(now.strftime('%m'), 16),
                                     int(now.strftime('%d'), 16), int(now.strftime('%H'), 16),
                                     int(now.strftime('%M'), 16), int(now.strftime('%S'), 16),
                                     int(now.strftime('%w'), 16)]))

        self.socket.send(payload)

        response = self.__recv_data()
        return response

    # Get name given to the device
    def get_dev_name(self):
        # Request name packet: 0xCCAA03180119
        payload = buffer(array('B', [0xCC, 0xAA, 0x03, 0x18, 0x01, 0x19]))
        self.socket.send(payload)
        response = self.__recv_data()

        return response[5:]

    # Change the devices given name
    def set_dev_name(self, name):
        if len(name) > 16:
            return False

        # Changed name packet: 0xCCAA121701(New name, max 16 chars)
        name_array = array('B', name)
        packet = array('B', [0xCC, 0xAA, 0x12, 0x17, 0x01])
        packet += name_array

        if len(packet) > 21:
            return False

        while len(packet) < 21:
            packet.append(0)

        payload = buffer(packet)
        self.socket.send(payload)
        response = self.__recv_data()
        return response

    # Set internal switch on or off
    # on = (bool) True for On, False for off
    def set_switch(self, on):
        if on:
            # ON Payload = 0xCCAA03010101
            payload = buffer(array('B', [0xCC, 0xAA, 0x03, 0x01, 0x01, 0x01]))
        else:
            # OFF Payload = 0xCCAA03010100
            payload = buffer(array('B', [0xCC, 0xAA, 0x03, 0x01, 0x01, 0x00]))

        self.socket.send(payload)
        response = self.__recv_data()

        response_bytes = memoryview(response).tolist()

        # Failed response packet: 0xCC55020101
        if response_bytes == [0xCC, 0x55, 0x02, 0x01, 0x01]:
            return False

        # Other possible response_bytes
        # ON:  cc:55:02:01:01:cc:55:03:02:01:01
        # OFF: cc:55:02:01:01:cc:55:03:02:01:00

        return True

    def __set_timer(self, btapstimer, create=True):
        name_array = array('B', btapstimer.name)

        start_time = btapstimer.get_start_time_bad_hex()
        end_time = btapstimer.get_end_time_bad_hex()
        repeat_day = btapstimer.get_repeat_day_byte()

        if create:
            create_byte = 0x20
        else:
            create_byte = 0x03

        packet = array('B', [0xCC, 0xAA, 0x1A, create_byte, 0x01, btapstimer.timer_id, repeat_day,
                             start_time[0], start_time[1], end_time[0], end_time[1], btapstimer.on])
        packet += name_array

        if len(packet) > 29:
            return False

        while len(packet) < 29:
            packet.append(0)

        payload = buffer(packet)
        self.socket.send(payload)
        response = self.__recv_data()
        return response

    # Create new timer
    # btapstimer = (BTApsTimer) containing all data you want in your new timer
    def create_timer(self, btapstimer):
        self.__set_timer(btapstimer, True)

    # Modify a timer that has already been created
    # btapstimer = (BTApsTimer) containing all data you want in your modified timer, not just the field you are changing
    def modify_timer(self, btapstimer):
        self.__set_timer(btapstimer, False)

    # Get current on/off state as well as a list of timers.
    # Returns: tuple(bool, timer_list). bool is current on/off state of switch,
    #                                   timer_list is a list of BTApsTimer objects
    def get_switch_state(self):
        # Request device state packet: 0xCCAA03120113
        payload = buffer(array('B', [0xCC, 0xAA, 0x03, 0x12, 0x01, 0x13]))
        self.socket.send(payload)

        response = self.__recv_data()
        on = memoryview(response).tolist()[7]
        response_list = []

        while True:
            response = self.__recv_data(23)
            if memoryview(response).tolist() == [0x00]:
                break
            else:
                response_list.append(response)

        timer_list = []
        for timer_response in response_list:
            timer_bytes = memoryview(timer_response).tolist()
            timer = BTapsTimer(timer_bytes[0], timer_response[7:])
            timer.set_repeat_days_byte(timer_bytes[1])
            timer.set_start_time(bad_hex_to_dec(timer_bytes[2]), bad_hex_to_dec(timer_bytes[3]))
            timer.set_end_time(bad_hex_to_dec(timer_bytes[4]), bad_hex_to_dec(timer_bytes[5]))
            timer.on = timer_bytes[6]

            timer_list.append(timer)

        return on, timer_list

    # Delete a timer
    # timer = (BTapsTimer) or (int) representing timer_id of timer you wish to delete
    def delete_timer(self, timer):
        if isinstance(timer, BTapsTimer):
            timer_id = timer.timer_id
        else:
            timer_id = timer

        # Delete timer packet: 0xCCAA04190101(timer id)
        payload = buffer(array('B', [0xCC, 0xAA, 0x04, 0x19, 0x01, 0x01, timer_id]))
        self.socket.send(payload)

        response = self.__recv_data()
        return response


# Timer object representing a single timer
class BTapsTimer:
    # timer_id: (int) ID of Timer
    # name: (str) Name of timer
    # start_time: (datetime.time) Start time for timer, only Hour and Minute matter
    # end_time: (datetime.time) End time for timer, only Hour and Minute matter
    # on: (bool) Enable or disable timer
    def __init__(self, timer_id, name, start_time=None, end_time=None, on=False):
        self.timer_id = None
        self.set_id(timer_id)

        self.name = None
        self.set_name(name)

        self.start_time = start_time
        self.end_time = end_time
        self.repeat_days = {'Mon': False, 'Tue': False, 'Wed': False,
                            'Thu': False, 'Fri': False, 'Sat': False, 'Sun': False}
        self.on = on

    # Set timer's name
    # name: (str) New name for timer
    def set_name(self, name):
        if len(name) <= 16:
            self.name = name

    # Set timer's ID
    # timer_id: (int) Set ID for timer
    def set_id(self, timer_id):
        if timer_id < 255:
            self.timer_id = timer_id

    # Set days on which timer repeats
    # mon,tue,wed,thu,fri,sat,sun: (bool) Enable timer repeat on said day
    def set_repeat_days(self, mon=None, tue=None, wed=None, thu=None, fri=None, sat=None, sun=None):
        if mon is not None:
            self.repeat_days['Mon'] = mon
        if tue is not None:
            self.repeat_days['Tue'] = tue
        if wed is not None:
            self.repeat_days['Wed'] = wed
        if thu is not None:
            self.repeat_days['Thu'] = thu
        if fri is not None:
            self.repeat_days['Fri'] = fri
        if sat is not None:
            self.repeat_days['Sat'] = sat
        if sun is not None:
            self.repeat_days['Sun'] = sun

    # Set timer's start time
    # hour: (int) Hour to start timer
    # minute: (int) Minute to start timer
    def set_start_time(self, hour, minute):
        self.start_time = datetime.time(hour, minute)

    # Set timer's end time
    # hour: (int) Hour to end timer
    # minute: (int) Minute to end timer
    def set_end_time(self, hour, minute):
        self.end_time = datetime.time(hour, minute)

    # Toggle timer on or off
    def toggle_on(self):
        self.on = not self.on

    # Get current timer start time in badly formatted hexadecimal format, see bad_hex_to_dec for an explanation
    def get_start_time_bad_hex(self):
        return int(self.start_time.strftime("%H"), 16), int(self.start_time.strftime("%M"), 16)

    # Get current timer end time in badly formatted hexadecimal format, see bad_hex_to_dec for an explanation
    def get_end_time_bad_hex(self):
        return int(self.end_time.strftime("%H"), 16), int(self.end_time.strftime("%M"), 16)

    # Get single byte representing days on which timer repeats
    def get_repeat_day_byte(self):
        if not self.repeat_days:
            return 0

        day_byte = 0
        if self.repeat_days['Mon']:
            day_byte ^= 0b00000010
        if self.repeat_days['Tue']:
            day_byte ^= 0b00000100
        if self.repeat_days['Wed']:
            day_byte ^= 0b00001000
        if self.repeat_days['Thu']:
            day_byte ^= 0b00010000
        if self.repeat_days['Fri']:
            day_byte ^= 0b00100000
        if self.repeat_days['Sat']:
            day_byte ^= 0b01000000
        if self.repeat_days['Sun']:
            day_byte ^= 0b10000000

        return day_byte

    # Set days on which timer repeats using a single byte
    def set_repeat_days_byte(self, byte):
        day_list = [False] * 7
        mon_byte = 0b00000010
        for i, _ in enumerate(day_list):
            day_byte = (mon_byte << i)
            if (byte & day_byte) == day_byte:
                day_list[i] = True

        self.set_repeat_days(day_list[0], day_list[1], day_list[2], day_list[3], day_list[4], day_list[5], day_list[6])