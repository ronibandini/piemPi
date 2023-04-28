# Piem machine
# Roni Bandini
# April, 2022
# Buenos Aires, Argentina

# Tm1637 CLK -> GPIO23 (Pin 16) Di0 -> GPIO24 (Pin 18)
# Printer tx -> rx and rx -> tx
# button GPIO 22

import decimal
import math
import random
import serial
import time
import sys
import RPi.GPIO as GPIO
import tm1637
import piemlogo as mypiemlogo
from Adafruit_Thermal import *
from datetime import datetime

Display = tm1637.TM1637(23,24,tm1637.BRIGHT_TYPICAL)
Display.Clear()
Display.SetBrightnes(5)

# send to printer
dontPrint=0

# how many decimals
#howManyDecimals=767
howManyDecimals=2000

# Paper width
columnLength=28

# Gpio button
buttonPin=22

# dictionary file
dictionaryFile="english.txt"

# pause between iterations
iterationPause=10

GPIO.setwarnings(False)  
GPIO.setup(buttonPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def saveLog(myLine):
  with open('/home/pi/piem/piemlog.txt',mode ='a') as file:
    file.write(myLine)
  file.close

def getWord(myCharacters):

  if int(myCharacters)==0:
    print("Received 0 decimal")
    return ""

  myWord=""
  myCounter=0
  myWordArray = [""]
  
  # new array with words of this length
  for x in lines:
    #print(x +": "+str(len(x)))
    if (len(x)-1)==int(myCharacters):
      #print(x)
      myWordArray.append(x)
      myCounter=myCounter+1

  # get a random index
  myIndex=random.randint(1,myCounter)
  #print("Length:"+str(myCharacters))
  #print("How many words:"+str(myCounter))
  #print("Random index:"+str(myIndex))
  #print("Word:"+myWordArray[myIndex])

  if myCounter==0:
    print("Array counter in 0!")
    return ":("

  wordToReturn=myWordArray[myIndex].strip()

  return wordToReturn

def piDecimal(d):

  myString=str(d)
  return myString[-1]

def computePi(n):
  
  decimal.getcontext().prec = n + 3
  #decimal.getcontext().Emax = 999999999
  
  C = 426880 * decimal.Decimal(10005).sqrt()
  K = decimal.Decimal(6)
  M = decimal.Decimal(1)
  X = decimal.Decimal(1)
  L = decimal.Decimal(13591409)
  S = L
  
  # For better precision, we calculate to n+3 and truncate the last two digits
  for i in range(1, n+3):
    M = decimal.Decimal(M* ((1728*i*i*i)-(2592*i*i)+(1104*i)-120)/(i*i*i))
    L = decimal.Decimal(545140134+L)
    X = decimal.Decimal(-262537412640768000*X)
    S += decimal.Decimal((M*L) / X)
    
  return str(C/S)[:-2] # Pi is C/S


#########################################################################################


uart = serial.Serial("/dev/serial0", baudrate=19200, timeout=3000)
printer = Adafruit_Thermal("/dev/serial0", 19200, timeout=5)

global lines

# read dictionary
text_file = open("/home/pi/piem/"+dictionaryFile, "r")
lines = text_file.readlines()
print("Words in database: "+str(len(lines)))
text_file.close()

print("PiemPi machine")
print("Roni Bandini - April 2023")

displayContent = [ 0, 0, 0, 0 ]

while GPIO.input(buttonPin) == GPIO.LOW:
  print("Paused")
  time.sleep(1)  
  Display.ShowDoublepoint(1) 
  Display.Show(displayContent)

Display.ShowDoublepoint(0)
Display.Show(displayContent)

if dontPrint==0:  	  
  printer.printBitmap(mypiemlogo.width, mypiemlogo.height, mypiemlogo.data)
  printer.setLineHeight(25)

start = time.time()

n = 1

widthCounter=0
myPrintLine=""
printWord=""

saveLog(str(datetime.now())+"\n") 

while True:


  while n <= howManyDecimals:

    while GPIO.input(buttonPin) == GPIO.LOW:
      print("Paused")
      time.sleep(1)
      Display.ShowDoublepoint(1)  
      Display.Show(displayContent)  

    Display.ShowDoublepoint(0)    

    # if higher than 9999, shows fixed 9999
    if n<9999:      
      nFilled=str(n).zfill(4)
      displayContent = [ int(nFilled[0:1]), int(nFilled[1:2]), int(nFilled[2:3]), int(nFilled[3:4]) ]
    else:
      displayContent = [ 9, 9, 9, 9 ]

    Display.ShowDoublepoint(0)
    Display.Show(displayContent)

    myPiComputed	=computePi(n)
    decimalValue	=piDecimal(myPiComputed)
    printWord		=getWord(decimalValue)
    print(str(myPiComputed)+"->"+printWord)
    #print("Width counter:"+str(widthCounter))
    #print("Print line:"+myPrintLine)

    if printWord=="":
      # zero decimal
      if dontPrint==0:
        print("0 decimal carriage")
        printer.println("") 
        saveLog("\n") 
    
    if widthCounter+int(decimalValue)<columnLength:
      widthCounter=widthCounter+int(decimalValue)
      #print("Adding to line: "+printWord)
      myPrintLine=myPrintLine+" "+printWord
      myPrintLine.replace("  ", " ")
    else:
      widthCounter=int(decimalValue)
      # print previous line, removing first space
      myPrintLine=myPrintLine.strip()
      print("Printing: "+myPrintLine)

      if dontPrint==0:
        printer.println(myPrintLine) 
        saveLog(myPrintLine+"\n")

      myPrintLine=printWord    

    n += 1

  # print remaining
  print("Printing remaining: "+myPrintLine)
  if dontPrint==0:
    printer.println(myPrintLine) 
    saveLog(myPrintLine+"\n") 

  end = time.time()
  elapsedTime=round((end - start), 2)

  if GPIO.input(buttonPin) == GPIO.HIGH and dontPrint==0:
    printer.println("")
    printer.println(myPiComputed)
    printer.println("")
    printer.println("Decimals: "+str(howManyDecimals)+" - Seconds: "+str(elapsedTime))
    printer.println("Version: 1.0 - @RoniBandini")
    printer.println("")
    printer.println("")
    printer.println("")
    printer.println("")

  saveLog("Decimals: "+str(howManyDecimals)+" - Seconds: "+str(elapsedTime)+"\n") 

  displayContent = [ 0, 0, 0, 0 ]
  
  Display.Show(displayContent)

  time.sleep(iterationPause)

  start = time.time()

  n = 1

  widthCounter=0
  myPrintLine=""
  printWord=""

  saveLog(str(datetime.now())+"\n") 



