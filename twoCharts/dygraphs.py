import json
import serial
import time
import sys
import binascii
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
import datetime

ser = serial.serial_for_url(str(sys.argv[1]), 115200)
try:
  if ser.isOpen():
    print("\nReady\n===========\n")
    ser.write(b'at+set_config=lorap2p:865000000:10:0:1:8:20\n')
    print(b'at+set_config=lorap2p:865000000:10:0:1:8:20\n')
    while True:
      z=ser.read_until()
      b=z.decode("utf-8").split("=")
      cmd=b[0]
      if cmd=="at+recv":
        print(z)
        c=b[1].split(':')
        data=c[0].split(',')
        rssi=data[0]
        snr=data[1]
        length=data[2]
        #print("Decoding "+c[1])
        enc=binascii.unhexlify(c[1].strip())
        cipher = AES.new(b'YELLOW SUBMARINEENIRAMBUS WOLLEY', AES.MODE_ECB)
        msg=""
        try:
          msg=cipher.decrypt(enc[0:len(enc)-28]).decode('ascii')
        except UnicodeDecodeError:
          print("UnicodeDecodeError after decrypting")
          print(enc)
          pass
        msg=msg.split("}")[0]+"}"
        try:
          x=json.loads(msg)
          dt= datetime.datetime.now()
          #S=f"{dt.strftime('%Y-%m-%d %H:%M:%S')},{x['H']},{x['T']}"
          S=dt.strftime('%Y-%m-%d %H:%M:%S')+","+str(x['H'])+","+str(x['T'])
          f = open("/var/www/html/dygraphs/dataHT.csv", "a")
          f.write(S)
          f.write("\n")
          print(S)
          f.close()
          #S=f"{dt.strftime('%Y-%m-%d %H:%M:%S')},{x['V']},{x['C']}"
          S=dt.strftime('%Y-%m-%d %H:%M:%S')+","+str(x['V'])+","+str(x['C'])
          f = open("/var/www/html/dygraphs/dataCV.csv", "a")
          f.write(S)
          f.write("\n")
          print(S)
          f.close()
        except ValueError:  # includes simplejson.decoder.JSONDecodeError
          print("Decoding JSON has failed")

except serial.SerialException as e:
  print("Exception")
  sys.stderr.write('could not open port {!r}: {}\n'.format(args.port, e))
  if ser.isOpen():
    ser.close()
