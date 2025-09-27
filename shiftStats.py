#!/usr/bin/env python3
import os,sys

magic=b'\x00\x00\x00\x00\x09\x10\x87\x02\x00'
#magic=b'\x00\x00\x00\x00\x09\x10\x87\x02\x01'
magic=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x09\x10'
endMagic=b'\x40'

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
   while not done:
      fh.seek(nextChunk,os.SEEK_SET)
      buff=fh.read(chunkSize)
      sres=buff.find(magic)
      if sres>=0:
         gpsStart=sres+nextChunk+len(magic)+3
         print("Found GPS magic at " + str(gpsStart))
         done=True
      else:
         if nextChunk==0:
            print("Failed to find magic. This means I was not able to find the start of the GPS data")
            sys.exit(1)
         nextChunk-=(chunkSize-len(magic))
         if nextChunk<0:
            nextChunk=0

   fh.seek(gpsStart,os.SEEK_SET)
   done=False
   recSize=53
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
   fh.close()
   return records


def adjustTimes(fname,records,offset):
   fh=open(fname,"rb+")
   for rec in records:
      intts=int.from_bytes(rec['data'][:4],byteorder='little')
      intnts=offset+intts
      bytets=intnts.to_bytes(4,'little')
      fh.seek(rec['addr'],os.SEEK_SET)
      fh.write(bytets)
   fh.close()


     
      

   
   

#fn="./VID_20250920_100517_00_006.insv"
fn="./VID_20250922_124309_00_007.insv"
#fn="./new.insv"
records=getGpsData(fn)
adjustTimes(fn,records,-60)


   
