#!/usr/bin/python3
import sys, termios, tty, select, time
import rclpy
from rclpy.node import Node
from rclpy.lifecycle import LifecycleNode
from controller_interfaces.msg import Keyboard
NUM_KEYS = 9
HELP = """
-----------
    w
a   s   d
  space
-----------
w/s เดินหน้า/ถอยหลัง | a/d เลี้ยว | space หยุด | i วางพิซซ่า | o บันทึก | q ออก | c clear 
"""

def kbd_enter_cbreak():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setcbreak(fd)
    return fd, old

def kbd_poll(fd, timeout=0.01):
    r, _, _ = select.select([sys.stdin], [], [], timeout)
    return sys.stdin.read(1) if r else None

def kbd_restore(fd, old):
    termios.tcsetattr(fd, termios.TCSADRAIN, old)

class Teleop(Node):
    def __init__(self):
        super().__init__('teleop_node')
        self.keypub = self.create_publisher(Keyboard, '/keyboard', 10)
        self.key_msg = Keyboard()
        self.key_msg.keyboard = [False] * NUM_KEYS
        self.clear_keys()
    def clear_keys(self): 
        self.key_msg.keyboard = [False]*9
    def handle_key(self, k: str):
        idx_map = {
            'w': 0,
            's': 1,
            'a': 2,
            'd': 3,
            ' ': 4,  
            'i': 5,
            'q': 6,
            'o' :7,
            'c' :8,
        }
        if k in idx_map:
            self.key_msg.keyboard[idx_map[k]] = True
            if k == 'q':
                return 'quit'
        return None

    def run(self):
        print(HELP)
        fd, old = kbd_enter_cbreak()
        try:
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.0)
                key = kbd_poll(fd, 0.01)
                self.clear_keys()
                if key is not None:
                    if self.handle_key(key) == 'quit':
                        break
                    self.keypub.publish(self.key_msg)
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            kbd_restore(fd, old)

def main(args=None):
    rclpy.init(args=args)
    node = Teleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
