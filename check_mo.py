
import struct

def check_mo(mo_file):
    with open(mo_file, 'rb') as f:
        buf = f.read()
        magic = struct.unpack('<I', buf[:4])[0]
        if magic != 0x950412de:
            print("Bad magic")
            return
        version, msgcount, masteridx, transidx = struct.unpack('<4I', buf[4:20])
        print(f"Version: {version}, MsgCount: {msgcount}")
        
        for i in range(msgcount):
            mlen, moff = struct.unpack('<II', buf[masteridx + i*8 : masteridx + i*8 + 8])
            tlen, toff = struct.unpack('<II', buf[transidx + i*8 : transidx + i*8 + 8])
            msg = buf[moff:moff+mlen]
            tmsg = buf[toff:toff+tlen]
            if mlen == 0:
                print(f"Header found! mlen={mlen}, tlen={tlen}")
                print(f"Header content: {tmsg[:100]}...")
            elif i < 5:
                print(f"Entry {i}: msgid='{msg}', msgstr='{tmsg}'")

if __name__ == '__main__':
    check_mo('locale/pt/LC_MESSAGES/django.mo')
