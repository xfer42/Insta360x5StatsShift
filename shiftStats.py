#!/usr/bin/env python3
#Insta360 X5 GPS Time Stats shift.
#Use this tool to shift the time on the GPS data in your insv file
#xfer42@hotmail.com

import os,sys


#I dont know how to officially find the GPS data, so Im looking for a specific byte sequence. If you know
#the proper way, then please let me know.

#magic=b'\x00\x00\x00\x00\x09\x10\x87\x02\x00'
#magic=b'\x00\x00\x00\x00\x09\x10\x87\x02\x01'
magic=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x09'
endMagic=b'\x40'


def isValidRecord(bdat):
   ets=bdat[:4]
   unk1=bdat[4:8]
   ts2=bdat[8:10]
   unk2=bdat[10:14]
   lat=bdat[14:18]
   unk3=bdat[18:23]
   long=bdat[23:27]
   unk4=bdat[27:33]
   speed=bdat[33:36]
   unk5=bdat[36:40]
   track=bdat[40:44]
   unk6=bdat[44:48]
   alt=bdat[48:51]
   unk7=bdat[51:52]
   unk8=bdat[52:53]
   if unk1==b'\x00\x00\x00\x00' and unk8==b'\x40':
      return True
   return False
   
def getGpsData(fname):
   fh=open(fname,'rb')
   fh.seek(0,os.SEEK_END)
   fileSize=fh.tell()

   #Get chunks of the end of the file and look for the magic
   #so we dont read a huge file from beginning to end
   done=False
   chunkSize=1024*1024
   nextChunk=fileSize-chunkSize
   gpsStart=0
   recSize=53
   while not done:
      fh.seek(nextChunk,os.SEEK_SET)
      buff=fh.read(chunkSize)
      sres=buff.find(magic)
      fh.seek(sres+nextChunk+len(magic)+4,os.SEEK_SET)
      btest=fh.read(recSize)
      if isValidRecord(btest):
         gpsStart=sres+nextChunk+len(magic)+4
         print("Found GPS magic at " + str(gpsStart))
         done=True
      else:
         if nextChunk==0:
            print("Failed to find magic. This means I was not able to find the start of the GPS data")
            sys.exit(1)
         nextChunk-=(chunkSize-(len(magic)+recSize))
         if nextChunk<0:
            nextChunk=0
   fh.seek(gpsStart,os.SEEK_SET)
   done=False
   records=[]
   cntr=0
   while not done:
      cntr+=1
      tmp=fh.read(recSize)
      done=True
      if tmp.endswith(endMagic):
         done=False
         recloc=fh.tell()-recSize
         records.append({"addr":recloc,"data":tmp})
         print(str(cntr)+":"+hex(recloc)+" " + tmp.hex())
      else:
         print(str(cntr)+":"+hex(recloc)+" " + tmp.hex())
   fh.close()
   return records

def adjustTimes(fname,records,offset):
   fh=open(fname,"rb+")
   for rec in records:
      intts=int.from_bytes(rec['data'][:4],byteorder='little')
      print(intts)
      intnts=offset+intts
      print(intts)
      bytets=intnts.to_bytes(4,'little')
      fh.seek(rec['addr'],os.SEEK_SET)
      fh.write(bytets)
   fh.close()

def help():
   print()
   print("Usage: ./shiftStats.py myvid.insv -t -30");
   print(" -h   This page.")
   print(" -t   Time offset in seconds. Example -t -61 (This will move the GPS data back 61 seconds)")
   print(" -f   Dont prompt. Just do it")
   print()
   sys.exit(0)

#fn="./VID_20250920_100517_00_006.insv"
#fn="./VID_20250922_124309_00_007.insv"
#fn="./new.insv"
fn=""
force=False
offset=0
args=sys.argv.copy()
args.pop(0)
if "-h" in args:
   help()
if "-f" in args:
   args.remove("-q")
   force=True
if "-t" in args:
   try:
      offset=int(args[args.index("-t")+1])
   except:
      print("Invalid offset. Enter a positive or negative number after -t")
      sys.exit(1)
   args.pop(args.index("-t")+1)
   args.remove("-t")

#Only support 1 file for now, but will probably support multiple later
try:
   fn=args[0]
except:
   print("Please specify a filename (.insv file).")
   sys.exit(1)


records=getGpsData(fn)
print("*** WARNING ***")
print("This will permenently modify " + fn +". I suggest you back it up.")
if force:
   #Do nothing
   pass
else:
   print("Found "+str(len(records))+" records. Press ENTER to proceed, or CTRL+C to abort.")
   input("...")

print("Adjusting times... " + str(offset))
adjustTimes(fn,records,offset)
print("Done.")


   
