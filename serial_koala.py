import serial
import time


class serialKoala:
    def koala(command):
        with serial.Serial('COM3', 115200) as ser:
            ser.close()
            ser.open()

            return_code = "\r\n"
            return_c = return_code.encode('ascii')

            # send the character to the device
            # (note that I happend a \r\n carriage return and line feed to the characters - this is requested by my device)
            input2 = command.encode('ascii')
            ser.write(input2)
            ser.write(return_c)
            out = ''
            # let's wait one second before reading output (let's give device time to answer)
            time.sleep(1)
            # while ser.inWaiting() > 0:
            #     out += ser.read(1).decode('utf-8')
            #
            # if out != '':
            #     print(">>" + out)
        ser.close()

