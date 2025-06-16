#!/usr/bin/env python3
"""
Ultimate Secure AI Agent v2.0
- Intelligent TOR routing
- AI/NLP security analysis
- Cross-platform (Win/Linux/Mac)
- Beautiful GUI + Powerful CLI
"""

import os
import sys
import time
import threading
import subprocess
import socket
import platform
import logging
from datetime import datetime
import psutil
import requests

# AI Core
try:
    from transformers import pipeline
    AI_READY = True
except ImportError:
    AI_READY = False

# TOR Connectivity
try:
    import stem
    from stem.control import Controller
    TOR_READY = True
except ImportError:
    TOR_READY = False

# GUI System
try:
    from PyQt5.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                                QMessageBox, QInputDialog)
    from PyQt5.QtGui import QIcon
    GUI_READY = True
except ImportError:
    GUI_READY = False

# ======================
# CORE AGENT FUNCTIONALITY
# ======================
class SecureAICore:
    def __init__(self):
        self.running = True
        self.tor_process = None
        self.setup_logging()
        self.logger = logging.getLogger('SecureAI')
        
    def setup_logging(self):
        """Configure advanced logging"""
        log_dir = os.path.join(os.path.expanduser("~"), ".secureai")
        os.makedirs(log_dir, exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, 'agent.log')),
                logging.StreamHandler()
            ]
        )

    def start_tor(self):
        """Smart TOR starter with auto-fallback"""
        if not TOR_READY:
            self.logger.warning("TOR not available - running in unprotected mode")
            return False
            
        try:
            tor_cmd = "tor" if platform.system() != "Windows" else "tor.exe"
            self.tor_process = stem.process.launch_tor_with_config(
                config={
                    'SocksPort': '9050',
                    'ControlPort': '9051',
                    'DataDirectory': os.path.join(os.path.expanduser("~"), ".tor")
                },
                tor_cmd=tor_cmd,
                timeout=300
            )
            self.logger.info("TOR started successfully")
            return True
        except Exception as e:
            self.logger.error(f"TOR failed: {str(e)}")
            return False

    def ai_analyze(self, text):
        """Smart text analysis with fallback"""
        if not AI_READY:
            return {"status": "error", "message": "AI engine not available"}
            
        try:
            analyzer = pipeline("text-classification", model="distilbert-base-uncased")
            return analyzer(text)
        except Exception as e:
            self.logger.error(f"AI analysis failed: {str(e)}")
            return {"status": "error", "message": str(e)}

    def security_scan(self):
        """Advanced system scanner"""
        threats = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'connections']):
                try:
                    info = proc.info
                    if info['cpu_percent'] > 90:
                        threats.append(f"High CPU: {info['name']} (PID: {info['pid']})")
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            self.logger.error(f"Scan failed: {str(e)}")
            
        return threats if threats else ["No immediate threats detected"]

    def run(self):
        """Main service loop"""
        self.logger.info("=== Secure AI Agent Started ===")
        self.start_tor()
        
        while self.running:
            try:
                threats = self.security_scan()
                if len(threats) > 1:  # More than just "No threats" message
                    self.logger.warning("Security Alert:\n" + "\n".join(threats))
                time.sleep(60)
            except KeyboardInterrupt:
                self.running = False
                
        self.logger.info("Agent stopped gracefully")

# ======================
# GUI INTERFACE
# ======================
class SecureAIGUI:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.core = SecureAICore()
        self.setup_tray()
        
    def setup_tray(self):
        """Create beautiful system tray interface"""
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(QIcon.fromTheme("security-high"))
        self.tray.setToolTip("Secure AI Agent")
        
        menu = QMenu()
        
        # Smart menu items
        menu.addAction("Security Status").triggered.connect(self.show_status)
        menu.addSeparator()
        
        if TOR_READY:
            menu.addAction("Renew TOR Identity").triggered.connect(self.renew_tor)
            
        if AI_READY:
            menu.addAction("AI Analysis").triggered.connect(self.run_analysis)
            
        menu.addAction("System Scan").triggered.connect(self.run_scan)
        menu.addSeparator()
        menu.addAction("Exit").triggered.connect(self.clean_exit)
        
        self.tray.setContextMenu(menu)
        self.tray.show()
        
        # Start core in background
        threading.Thread(target=self.core.run, daemon=True).start()
        
    def renew_tor(self):
        try:
            with Controller.from_port(port=9051) as ctrl:
                ctrl.authenticate()
                ctrl.signal(Signal.NEWNYM)
            self.show_message("TOR Identity", "Successfully renewed anonymous identity")
        except Exception as e:
            self.show_message("Error", f"TOR renewal failed: {str(e)}", is_error=True)

    def run_analysis(self):
        text, ok = QInputDialog.getText(None, "AI Security Analysis", "Enter text to analyze:")
        if ok and text:
            result = self.core.ai_analyze(text)
            self.show_message("Analysis Result", str(result))

    def run_scan(self):
        threats = self.core.security_scan()
        self.show_message("System Scan", "\n".join(threats))

    def show_status(self):
        status = [
            f"Agent: {'Running' if self.core.running else 'Stopped'}",
            f"TOR: {'Active' if self.core.tor_process else 'Inactive'}",
            f"AI: {'Ready' if AI_READY else 'Unavailable'}"
        ]
        self.show_message("Current Status", "\n".join(status))

    def show_message(self, title, message, is_error=False):
        """Smart notification display"""
        self.tray.showMessage(
            title,
            message,
            QSystemTrayIcon.Critical if is_error else QSystemTrayIcon.Information,
            5000
        )

    def clean_exit(self):
        self.core.running = False
        self.app.quit()

# ======================
# COMMAND LINE INTERFACE
# ======================
def cli_main():
    print(r"""
    ____ ___  ____  ___    _____ ____    ____ ___ 
   / __ `__ \/ __ \/ _ \  / ___// __ \  / __ `__ \
  / / / / / / /_/ /  __/ (__  ) / / / / / / / / /
 /_/ /_/ /_/ .___/\___/ /____/_/ /_/ /_/ /_/ /_/ 
          /_/                                      
    """)
    
    core = SecureAICore()
    
    try:
        print("[*] Starting Secure AI Agent (Ctrl+C to stop)")
        core.run()
    except KeyboardInterrupt:
        print("\n[!] Shutting down...")
    finally:
        print("[*] Agent stopped")

# ======================
# LAUNCHER
# ======================
if __name__ == '__main__':
    # Check for single instance
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(('127.0.0.1', 65432))
    except socket.error:
        print("Error: Another instance is already running", file=sys.stderr)
        sys.exit(1)
        
    # Launch appropriate interface
    if GUI_READY and '--cli' not in sys.argv:
        try:
            gui = SecureAIGUI()
            sys.exit(gui.app.exec_())
        except Exception as e:
            print(f"GUI failed: {str(e)} - falling back to CLI")
            cli_main()
    else:
        cli_main()
