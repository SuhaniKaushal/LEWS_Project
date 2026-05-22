import huaweisms.api.user
import huaweisms.api.wlan
import huaweisms.api.sms
import huaweisms.api.ussd
import huaweisms.api.device
#from collections import OrderedDict

try:
    ctx = huaweisms.api.user.quick_login("admin", "Root@123")
    print(ctx)
    print('NO PROBLEM')
except Exception as e:
    print("SMS CANT SEND WRITE NOW3",e)
    
#print(ctx)
#Till this line it works Great



#This ussd code is to check balance: *101#
#This code doesn't work, no matter what I changed:
def send_sms(msg):
  try:
      #print('msg',msg)
      r = huaweisms.api.sms.send_sms(ctx,"9643547670",msg)
      #print(type(r))
      #print(r.keys())
      #print(r['type'])
      #print(r['response'])
      if(r['response']=='OK'):
        print('SMS SENT')
      else:
        print('cant sent SMS')
 
      
  except Exception as e:
      print("SMS CAN'T SENT WRITE NOW_",e)
      try:
        ctx3 = huaweisms.api.user.quick_login("admin", "Root@123")
        print('ctx3 is',ctx3)
        r = huaweisms.api.sms.send_sms(ctx3,"9643547670",msg)
        if(r['response']=='OK'):
          print('SMS SENT in RETRY')
      except:
        print('CANT SENT')

#print("\n........................\n")
if __name__ == "__main__":
  count=0;
  while count<3:
    send_sms('THERE IS A POSSSIBILITY OF LANDSLIDE AT netala'+'  '+'n3'+'. SENSOR name IS pitch1 having value is '+"20"+' At time 12/06/2020, 03:42:02')
    print('\n\n')
    count=count+1
