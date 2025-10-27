import tkinter as tk
from tkinter import messagebox, simpledialog
import requests
import threading
import time
import socket
import logging
from werkzeug.security import check_password_hash
import nfc  # For RFID/NFC reading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class POSKiosk:
    def __init__(self, root):
        self.root = root
        self.root.title("POS Kiosk")
        self.root.attributes('-fullscreen', True)
        self.mode = 'kiosk_staff'  # default mode
        self.locked = True
        self.server_url = None
        self.items = []
        self.cart = []
        self.current_user = None
        self.rfid_sim = ''  # simulate RFID
        self.kiosk_id = None
        self.error_mode_active = False
        self.discover_server()
        self.setup_ui()

    def discover_server(self):
        try:
            # Broadcast to find server
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(5)
            sock.sendto(b"DISCOVER_POS_SERVER", ("<broadcast>", 5001))
            data, addr = sock.recvfrom(1024)
            if data == b"POS_SERVER_HERE":
                self.server_url = f"http://{addr[0]}:5000"
                logger.info(f"Server discovered at {self.server_url}")
            sock.close()
        except Exception as e:
            logger.error(f"Server discovery failed: {e}")
            self.server_url = 'http://localhost:5000'  # fallback

    def setup_ui(self):
        # Touch-friendly: larger fonts, buttons, padding, colors
        self.lock_screen = tk.Frame(self.root, bg='lightblue')
        self.main_screen = tk.Frame(self.root, bg='lightgreen')
        self.error_screen = tk.Frame(self.root, bg='red')

        # Lock screen
        tk.Label(self.lock_screen, text="Locked", font=('Arial', 36, 'bold'), bg='lightblue').pack(pady=50)
        self.mode_var = tk.StringVar(value='kiosk_staff')
        mode_menu = tk.OptionMenu(self.lock_screen, self.mode_var, 'kiosk_staff', 'teacher', 'admin')
        mode_menu.config(font=('Arial', 24), width=20, height=2, bg='white')
        mode_menu.pack(pady=20)
        unlock_btn = tk.Button(self.lock_screen, text="Unlock with Password", command=self.unlock_password, font=('Arial', 24), height=2, width=25, bg='white')
        unlock_btn.pack(pady=20)
        rfid_btn = tk.Button(self.lock_screen, text="Scan RFID", command=self.scan_rfid, font=('Arial', 24), height=2, width=25, bg='white')
        rfid_btn.pack(pady=20)
        self.lock_screen.pack(fill=tk.BOTH, expand=True)

        # Main screen
        lock_btn = tk.Button(self.main_screen, text="Lock", command=self.lock, font=('Arial', 20), height=2, width=15, bg='white')
        lock_btn.pack(pady=10)
        tk.Label(self.main_screen, text="Items", font=('Arial', 24), bg='lightgreen').pack()
        self.item_list = tk.Listbox(self.main_screen, font=('Arial', 20), height=10, bg='white')
        self.item_list.pack(fill=tk.X, padx=20, pady=10)
        add_btn = tk.Button(self.main_screen, text="Add to Cart", command=self.add_to_cart, font=('Arial', 24), height=2, width=20, bg='white')
        add_btn.pack(pady=10)
        tk.Label(self.main_screen, text="Cart", font=('Arial', 24), bg='lightgreen').pack()
        self.cart_list = tk.Listbox(self.main_screen, font=('Arial', 20), height=5, bg='white')
        self.cart_list.pack(fill=tk.X, padx=20, pady=10)
        checkout_btn = tk.Button(self.main_screen, text="Checkout", command=self.checkout, font=('Arial', 24), height=2, width=20, bg='white')
        checkout_btn.pack(pady=10)
        if self.mode in ['teacher', 'admin']:
            manual_btn = tk.Button(self.main_screen, text="Manual Charge", command=self.manual_charge, font=('Arial', 24), height=2, width=20, bg='white')
            manual_btn.pack(pady=10)
        if self.mode == 'admin':
            manage_btn = tk.Button(self.main_screen, text="Manage Items", command=self.manage_items, font=('Arial', 24), height=2, width=20, bg='white')
            manage_btn.pack(pady=10)
            custom_btn = tk.Button(self.main_screen, text="Custom Charge", command=self.custom_charge, font=('Arial', 24), height=2, width=20, bg='white')
            custom_btn.pack(pady=10)

        # Error screen
        tk.Label(self.error_screen, text="Error Mode: Cannot connect to server", font=('Arial', 24), bg='red').pack(pady=20)
        retry_btn = tk.Button(self.error_screen, text="Retry", command=self.retry_connection, font=('Arial', 24), height=2, width=20, bg='white')
        retry_btn.pack()

        self.load_items()

    def unlock_password(self):
        try:
            password = simpledialog.askstring("Password", "Enter password:")
            if password:
                if self.mode_var.get() == 'kiosk_staff' and self.check_password('kiosk', password):
                    self.unlock('kiosk_staff')
                elif self.mode_var.get() == 'teacher' and self.check_password('teacher', password):
                    self.unlock('teacher')
                elif self.mode_var.get() == 'admin' and self.check_password('admin', password):
                    self.unlock('admin')
        except Exception as e:
            logger.error(f"Error unlocking with password: {e}")
            self.enter_error_mode()

    def check_password(self, mode, password):
        try:
            response = requests.get(f'{self.server_url}/api/kiosks')
            kiosks = response.json()
            for kiosk in kiosks:
                if kiosk['id'] == self.kiosk_id:
                    if mode == 'kiosk' and check_password_hash(kiosk['password_kiosk'], password):
                        return True
                    elif mode == 'teacher' and check_password_hash(kiosk['password_teacher'], password):
                        return True
                    elif mode == 'admin' and check_password_hash(kiosk['password_admin'], password):
                        return True
        except Exception as e:
            logger.error(f"Error checking password: {e}")
            self.enter_error_mode()
        return False

    def scan_rfid(self):
        try:
            # Try hardware RFID reader first
            clf = nfc.ContactlessFrontend('usb')
            tag = clf.connect(rdwr={'on-connect': lambda tag: False})
            if tag:
                self.rfid_sim = str(tag.identifier).upper()
                self.unlock_with_rfid()
            clf.close()
        except Exception as e:
            logger.warning(f"Hardware RFID failed: {e}, falling back to simulation")
            # Fallback to simulation
            rfid = simpledialog.askstring("RFID", "Enter RFID:")
            if rfid:
                self.rfid_sim = rfid
                self.unlock_with_rfid()

    def unlock_with_rfid(self):
        try:
            response = requests.get(f'{self.server_url}/api/users')
            users = response.json()
            for user in users:
                if user['rfid'] == self.rfid_sim:
                    self.unlock(user['privilege'])
                    self.current_user = user
                    break
        except Exception as e:
            logger.error(f"Error unlocking with RFID: {e}")
            self.enter_error_mode()

    def unlock(self, mode):
        self.mode = mode
        self.locked = False
        self.lock_screen.pack_forget()
        self.main_screen.pack(fill=tk.BOTH, expand=True)

    def lock(self):
        self.locked = True
        self.main_screen.pack_forget()
        self.lock_screen.pack(fill=tk.BOTH, expand=True)

    def load_items(self):
        try:
            response = requests.get(f'{self.server_url}/api/items')
            self.items = response.json()
            self.item_list.delete(0, tk.END)
            for item in self.items:
                self.item_list.insert(tk.END, f"{item['name']} - ${item['price']}")
        except Exception as e:
            logger.error(f"Error loading items: {e}")
            self.enter_error_mode()

    def add_to_cart(self):
        try:
            selection = self.item_list.curselection()
            if selection:
                item = self.items[selection[0]]
                self.cart.append(item)
                self.cart_list.insert(tk.END, f"{item['name']} - ${item['price']}")
        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            self.enter_error_mode()

    def checkout(self):
        try:
            if not self.current_user:
                messagebox.showerror("Error", "No user selected")
                return
            total = sum(item['price'] for item in self.cart)
            for item in self.cart:
                requests.post(f'{self.server_url}/api/sales', json={
                    'user_id': self.current_user['id'],
                    'item_id': item['id'],
                    'quantity': 1,
                    'total_price': item['price']
                })
            self.cart = []
            self.cart_list.delete(0, tk.END)
            messagebox.showinfo("Success", f"Checkout complete. Total: ${total}")
        except Exception as e:
            logger.error(f"Error during checkout: {e}")
            self.enter_error_mode()

    def manual_charge(self):
        try:
            user_id = simpledialog.askinteger("User ID", "Enter user ID:")
            amount = simpledialog.askfloat("Amount", "Enter amount:")
            if user_id and amount:
                requests.post(f'{self.server_url}/api/sales', json={
                    'user_id': user_id,
                    'item_id': 0,  # dummy
                    'quantity': 1,
                    'total_price': amount
                })
        except Exception as e:
            logger.error(f"Error in manual charge: {e}")
            self.enter_error_mode()

    def custom_charge(self):
        try:
            amount = simpledialog.askfloat("Amount", "Enter custom amount:")
            if amount:
                # Assume admin can charge custom
                pass
        except Exception as e:
            logger.error(f"Error in custom charge: {e}")
            self.enter_error_mode()

    def manage_items(self):
        try:
            # Simple add item
            name = simpledialog.askstring("Item Name", "Enter item name:")
            price = simpledialog.askfloat("Price", "Enter price:")
            if name and price:
                requests.post(f'{self.server_url}/api/items', json={'name': name, 'price': price})
                self.load_items()
        except Exception as e:
            logger.error(f"Error managing items: {e}")
            self.enter_error_mode()

    def enter_error_mode(self):
        if not self.error_mode_active:
            self.error_mode_active = True
            self.lock()
            self.lock_screen.pack_forget()
            self.error_screen.pack(fill=tk.BOTH, expand=True)

    def retry_connection(self):
        self.error_mode_active = False
        self.error_screen.pack_forget()
        self.lock_screen.pack(fill=tk.BOTH, expand=True)
        self.discover_server()
        self.load_items()

if __name__ == '__main__':
    try:
        root = tk.Tk()
        app = POSKiosk(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Failed to start kiosk: {e}")
