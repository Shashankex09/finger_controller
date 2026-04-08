import serial
import time

# Test script to send servo commands to ESP
# Run this to test your ESP-servo connection before using face detection

SERIAL_PORT = "COM21"  # Change this to match your ESP's COM port
BAUD_RATE = 115200

def send_angle(ser, angle):
    """Send angle command to ESP"""
    cmd = f"A{int(angle):03d}\n"
    ser.write(cmd.encode())
    print(f"Sent: {cmd.strip()}")

def main():
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)
        print(f"Connected to {SERIAL_PORT} at {BAUD_RATE} baud")
        print("Testing servo movement...")
        print("Commands: 'test' for sweep, 'angle X' for specific angle, 'quit' to exit")

        while True:
            cmd = input("Command: ").strip().lower()

            if cmd == 'quit':
                break
            elif cmd == 'test':
                print("Sweeping servo...")
                for angle in range(20, 161, 20):
                    send_angle(ser, angle)
                    time.sleep(0.5)
                for angle in range(160, 19, -20):
                    send_angle(ser, angle)
                    time.sleep(0.5)
                send_angle(ser, 90)  # Center
            elif cmd.startswith('angle '):
                try:
                    angle = int(cmd.split()[1])
                    if 20 <= angle <= 160:
                        send_angle(ser, angle)
                    else:
                        print("Angle must be between 20-160")
                except ValueError:
                    print("Invalid angle. Use: angle 90")
            else:
                print("Unknown command. Use: test, angle X, or quit")

        ser.close()
        print("Disconnected")

    except Exception as e:
        print(f"Error: {e}")
        print("Make sure:")
        print("- ESP is connected and powered on")
        print("- COM port is correct")
        print("- ESP code is uploaded and running")

if __name__ == "__main__":
    main()