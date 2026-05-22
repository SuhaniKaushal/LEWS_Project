import serial
import time

# -------------------- Configuration --------------------
SERIAL_PORT = '/dev/ttyUSB3'  # replace with your Zigbee USB port
BAUD_RATE = 115200
# -------------------------------------------------------

def extract_ascii_payload(packet):
    """
    Extract human-readable ASCII strings from the binary packet.
    Ignores non-ASCII bytes.
    """
    try:
        # decode ASCII, ignore bytes that can't be decoded
        payload = packet.decode('ascii', errors='ignore')
        # strip header/footer like DBG and EE if present
        payload = payload.replace('DBG', '').replace('EE', '').strip()
        return payload
    except Exception as e:
        print("Error decoding payload:", e)
        return ""

def main():
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.5)
    buffer = b''

    print("Waiting for Zigbee packets...")

    while True:
        # read all available bytes
        chunk = ser.read(ser.inWaiting() or 1)
        if chunk:
            buffer += chunk

            # process all complete packets in buffer
            while b'DBG' in buffer and b'EE' in buffer:
                start = buffer.find(b'DBG')
                end = buffer.find(b'EE', start) + 2  # include EE
                packet = buffer[start:end]
                buffer = buffer[end:]  # remove processed packet

                ascii_payload = extract_ascii_payload(packet)
                if ascii_payload:
                    print("ASCII Payload:", ascii_payload)

        else:
            time.sleep(0.05)

if __name__ == "__main__":
    main()
