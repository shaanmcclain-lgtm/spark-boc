import time
import threading
from sparkybotmini import SparkyBotMini
from pynput import keyboard

# Robot initialization
mr_sparky = SparkyBotMini(port="/dev/ttyUSB0")

# Control settings
current_power = 50  # Default power level (1-100)
running = True
key_pressed = None


def set_power():
    """Allow user to set motor power level before starting"""
    global current_power
    while True:
        try:
            power = int(input("Enter motor power level (1-100): "))
            if 1 <= power <= 100:
                current_power = power
                print(f"? Motor power set to {current_power}%")
                break
            else:
                print("? Please enter a value between 1 and 100")
        except ValueError:
            print("? Invalid input. Please enter a number between 1 and 100")


def stop_motors():
    """Stop all motors"""
    mr_sparky.set_motor(0, 0, 0, 0)


def move_forward(power):
    """Move forward - all motors forward"""
    mr_sparky.set_motor(power, power, power, power)
    print(f"? Moving forward at {power}%")


def move_backward(power):
    """Move backward - all motors backward"""
    mr_sparky.set_motor(-power, -power, -power, -power)
    print(f"? Moving backward at {power}%")


def move_left_strafe(power):
    """Strafe left - M1 back, M2 forward, M3 forward, M4 back"""
    mr_sparky.set_motor(-power, power, power, -power)
    print(f"? Strafing left at {power}%")


def move_right_strafe(power):
    """Strafe right - reverse of left strafe"""
    mr_sparky.set_motor(power, -power, -power, power)
    print(f"? Strafing right at {power}%")


def on_press(key):
    """Handle key press events"""
    global key_pressed, running
    
    try:
        if key == keyboard.Key.w:
            key_pressed = 'w'
            move_forward(current_power)
        elif key == keyboard.Key.s:
            key_pressed = 's'
            move_backward(current_power)
        elif key == keyboard.Key.a:
            key_pressed = 'a'
            move_left_strafe(current_power)
        elif key == keyboard.Key.d:
            key_pressed = 'd'
            move_right_strafe(current_power)
        elif key == keyboard.Key.esc:
            running = False
            print("? Exiting...")
    except AttributeError:
        pass


def on_release(key):
    """Handle key release events"""
    global key_pressed
    
    try:
        if key in [keyboard.Key.w, keyboard.Key.s, keyboard.Key.a, keyboard.Key.d]:
            stop_motors()
            key_pressed = None
            print("? Stopped")
    except AttributeError:
        pass


def main():
    """Main control loop"""
    global running
    
    print("=" * 50)
    print("? SparkyBotMini Omni Drive WASD Control")
    print("=" * 50)
    print("Controls:")
    print("  W - Move Forward")
    print("  S - Move Backward")
    print("  A - Strafe Left")
    print("  D - Strafe Right")
    print("  ESC - Exit")
    print("=" * 50)
    
    # Get power level from user
    set_power()
    
    # Connect to robot
    if not mr_sparky.connect():
        print("? Failed to connect to robot")
        return
    
    print("? Robot connected. Starting keyboard listener...")
    print("? Press any key to start (W/A/S/D to move, ESC to exit)")
    
    # Start keyboard listener
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.start()
    
    try:
        # Keep program running until ESC is pressed
        while running:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n? Interrupted by user")
    
    finally:
        # Cleanup
        stop_motors()
        listener.stop()
        mr_sparky.disconnect()
        print("? Goodbye!")


if __name__ == "__main__":
    main()
