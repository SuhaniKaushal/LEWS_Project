#!/usr/bin/env python3
import serial
import time
import glob

BAUD = 115200

# ✅ LIST OF 5 PEOPLE (use international format)
PHONE_NUMBERS = [
    "+91879159920X",
    "+91XXXXXXXXXX",
    "+91XXXXXXXXXX",
    "+91XXXXXXXXXX",
    "+91XXXXXXXXXX",
]

WARNING_MESSAGE = (
    "⚠️ ALERT ⚠️\n"
    "There is a POSSIBLE RISK OF LANDSLIDE in your area.\n"
    "Please stay alert and follow safety instructions."
)

# --------------------------------------------------

def find_at_port():
    """Find the Quectel AT command port"""
    ports = sorted(glob.glob("/dev/ttyUSB*"))
    for port in ports:
        try:
            ser = serial.Serial(port, BAUD, timeout=2)
            ser.write(b"AT\r\n")
            time.sleep(0.5)
            resp = ser.read_all()
            ser.close()
            if b"OK" in resp:
                print(f"✅ AT port found: {port}")
                return port
        except Exception:
            continue
    return None


def send_sms(phone_number, message):
    port = find_at_port()
    if not port:
        print("❌ ERROR: No AT port found.")
        return False

    try:
        ser = serial.Serial(port, BAUD, timeout=5)

        # Text mode
        ser.write(b"AT+CMGF=1\r\n")
        time.sleep(1)

        # Set recipient
        ser.write(f'AT+CMGS="{phone_number}"\r\n'.encode())
        time.sleep(1)

        # Send message + CTRL-Z
        ser.write(message.encode("utf-8") + b"\x1A")
        time.sleep(6)

        response = ser.read_all().decode(errors="ignore")
        ser.close()

        if "OK" in response:
            print(f"✅ SMS sent to {phone_number}")
            return True
        else:
            print(f"❌ Failed to send SMS to {phone_number}")
            print("Modem response:", response)
            return False

    except Exception as e:
        print(f"❌ Error sending SMS to {phone_number}: {e}")
        return False


# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == "__main__":
    print("=== EC200U-CN SMS Warning System ===")

    for number in PHONE_NUMBERS:
        send_sms(number, WARNING_MESSAGE)
        time.sleep(3)  # avoid network throttling
