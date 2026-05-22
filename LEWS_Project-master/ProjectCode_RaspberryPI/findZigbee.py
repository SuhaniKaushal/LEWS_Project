import serial.tools.list_ports

ZIGBEE_VIDS = {
    0x10C4,  # Silicon Labs (Sonoff, SkyConnect)
    0x0451,  # Texas Instruments (CC2531/CC2652)
    0x1CF1,  # Dresden Elektronik (ConBee)
    0x0403,  # FTDI
}

def find_zigbee_ports():
    ports = serial.tools.list_ports.comports()
    zigbee_ports = []

    for port in ports:
        if port.device.startswith(("/dev/ttyUSB", "/dev/ttyACM")):
            if port.vid in ZIGBEE_VIDS:
                zigbee_ports.append(port)

    return zigbee_ports, ports


if __name__ == "__main__":
    zigbee, all_ports = find_zigbee_ports()

    print("All serial ports:")
    for p in all_ports:
        print(f"  {p.device} - {p.description}")

    print("\nZigbee candidates:")
    if not zigbee:
        print("  ❌ No Zigbee dongle detected")
    else:
        for p in zigbee:
            print(f"  ✅ {p.device}")
            print(f"     Description : {p.description}")
            print(f"     VID:PID     : {p.vid}:{p.pid}")
