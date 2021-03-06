import time
import numpy as np
import liblo as lo
import grovepi
import grove_oled
from adxl345 import ADXL345
from optparse import OptionParser



usage = "python sensor-osc.py --oscip 127.0.0.1 --oscport 7878 --with_accel 1 --with_oled 0 --with_pulse 1"
parser = OptionParser(usage=usage)
parser.add_option("-o", "--oscip", 
                  dest="oscip", type='string', default="127.0.0.1",
                  help="IP address to send OSC message to")
parser.add_option("-p", "--oscport", 
                  dest="oscport", type='int', default=7878,
                  help="host port")
parser.add_option("-a", "--with_accel", 
                  dest="withAccel", type='int', default=1,
                  help="Is a Grove Accelerometer ADXL345 connected via I2C?")
parser.add_option("-P", "--with_pulse", 
                  dest="withPulse", type='int', default=1,
                  help="Is a pulse sensor connected to A0?")
parser.add_option("-d", "--debug", 
                  dest="printDebug", type='int', default=0,
                  help="Print the sensor values to stdout?")

				  
(options, args) = parser.parse_args()

outputAddress = lo.Address(options.oscip, options.oscport)
global axes

if options.withAccel:	
	adxl345 = ADXL345()
	axes = adxl345.getAxes(True)



analogdata = np.zeros(3)
digitaldata = np.zeros(1)
timestamps = np.zeros(3)


			
			
while True:

	# this is specific to GrovePi Zero.  Additional pins may be used.
	# See https://www.dexterindustries.com/GrovePi/engineering/port-description/
	# for unlocking more I/O

	analogdata[0] = grovepi.analogRead(0)
	analogdata[1] = grovepi.analogRead(1)
	analogdata[2] = grovepi.analogRead(2)
        timestamps[0] = time.time()  # let's take a timestamp, in case we want to use it someday
	analogMessage = lo.Message('/grove/analog', analogdata[0], analogdata[1], analogdata[2])
	lo.send(outputAddress, analogMessage)
	
	
	digitaldata[0] = grovepi.digitalRead(3) 
        timestamps[1] = time.time()
	digitalMessage = lo.Message('/grove/digital', digitaldata[0])
	lo.send(outputAddress, digitalMessage)
	
	if options.printDebug:
		print("analog: A0 %.3f, A1 %.3f, A2 %.3f" % (analogdata[0], analogdata[1], analogdata[2]))
		print("digital: D3 %d" % (digitaldata[0]))

	if options.withPulse:
		pulseMessage = lo.Message('/grove/pulsesensor', analogdata[0])
		lo.send(outputAddress, pulseMessage)		
		
	if options.withAccel:
		timestamps[2] = time.time()
		axes = adxl345.getAxes(True)
		accelMessage = lo.Message('/grove/accel', axes['x'], axes['y'], axes['z'])
		lo.send(outputAddress, accelMessage)

		if options.printDebug:
			print("accel: x = %.3fG, y = %.3fG, z = %.3fG" % ( axes['x'], axes['y'], axes['z']))
		

		

		
		
