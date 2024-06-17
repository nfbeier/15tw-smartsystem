import time
import serial

class XGS600Driver:
    '''
    Driver for the Agilent XGS600 Vacuum Gauge Controller
    '''

    def __init__(self,port = "COM3",timeout = 2.0):
        self.serial = serial.Serial(port)
        self.timeout = timeout

    def xgs_comm(self, command, expect_reply=True):
        """Implements basic communication"""
        # Write command
        self.serial.read(self.serial.inWaiting())  # Clear waiting characters
        comm = "#00" + command + "\r"  # #00 is RS232 communication and #aa is RS485
        self.serial.write(comm.encode('ascii'))

        # Read reply if requested
        # Expected reply is always '>'+reply+'\r'
        # A reply can either be hex value or string or list of strings
        t_start_reply = time.time()
        time.sleep(0.25)
        if expect_reply:
            gathered_reply = ''
            number_of_bytes = self.serial.inWaiting()
            gathered_reply += self.serial.read(number_of_bytes).decode()
            while not gathered_reply.endswith('\r'):
                print(
                    "Waiting for rest of reply, reply so far is: ", repr(gathered_reply)
                )
                number_of_bytes = self.serial.inWaiting()
                gathered_reply += self.serial.read(number_of_bytes).decode()

                if time.time() - t_start_reply > self.timeout:
                    raise TimeoutError
                time.sleep(0.25)

            return gathered_reply.replace('>', '').replace('\r', '')
        
    def read_all_pressures(self):
        """Read pressure from all sensors"""
        pressures = [-3]
        error = 1
        while (error > 0) and (error < 10):
            pressure_string = self.xgs_comm("0F")
            if len(pressure_string) > 0:
                error = 0
                temp_pressure = pressure_string.replace(' ', '').split(',')
                pressures = []
                for press in temp_pressure:
                    if press == 'OPEN':
                        pressures.append('OPEN')
                    else:
                        try:
                            pressures.append((float)(press))
                        except ValueError:
                            pressures.append(-2)
            else:
                time.sleep(0.2)
                error = error + 1
        return pressures
    
    def list_all_gauges(self):
        """
        List all installed gauge cards
        The FRG720 Gauge isn't listed in the manual, but it reads out as 4C
        """
        gauge_string = self.xgs_comm("01")
        gauges = ""
        for gauge_number in range(0, len(gauge_string), 2):
            gauge = gauge_string[gauge_number : gauge_number + 2]
            if gauge == "FE":
                gauges = gauges + str(gauge_number / 2) + ": Empty Slot\n"
            if gauge == "4C":
                gauges = gauges + str(gauge_number / 2) + ": FRG720\n"
            if gauge == "10":
                gauges = gauges + str(gauge_number / 2) + ": Hot Filament Gauge\n"
            if gauge == "40":
                gauges = gauges + str(gauge_number / 2) + ": Convection Board\n"
            if gauge == "3A":
                gauges = gauges + str(gauge_number / 2) + ": Inverted Magnetron Board\n"
        return gauges

    def read_pressure(self, gauge_id):
        """Read the pressure from a specific gauge.
        gauge_id is represented as Uxxxxx and xxxxx is the userlabel"""
        pressure = self.xgs_comm('02' + gauge_id)
        try:
            val = float(pressure)
        except ValueError:
            val = -1.0
        return val
  
    def read_pressure_unit(self):
        """Read which pressure unit is used"""
        gauge_string = self.xgs_comm("13")
        unit = gauge_string.replace(' ', '')
        if unit == "00":
            unit = "Torr"
        if unit == "01":
            unit = "mBar"
        if unit == "02":
            unit = "Pascal"
        return unit
    
if __name__ == '__main__':
    XGS = XGS600Driver()
    print(XGS)
    print(XGS.read_pressure("UMAIN1"))