import sys
import time
import configparser
import subprocess
from PyQt6.QtWidgets import QApplication, QMainWindow, QSplashScreen, QStatusBar, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtWebEngineWidgets import QWebEngineView


class SplashScreen(QSplashScreen):
    def __init__(self):
        super().__init__(QPixmap("splash.png"))
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint)

    def drawContents(self, painter: QPainter):
        painter.setPen(Qt.GlobalColor.white)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "Loading...")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Linux App")
        self.setGeometry(100, 100, 1200, 800)
        
        # Set dark mode with red hues
        self.setStyleSheet("""
            QMainWindow, QTabWidget, QStatusBar {
                background-color: #1e1e1e;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #ff4d4d;
            }
            QTabBar::tab {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 8px;
            }
            QTabBar::tab:selected {
                background-color: #ff4d4d;
            }
        """)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)
               
        # Create Ollama tab
        self.ollama_tab = QWidget()
        self.ollama_layout = QVBoxLayout()
        self.ollama_browser = QWebEngineView()
        self.ollama_browser.setUrl(QUrl("https://ollama.ai"))
        self.ollama_layout.addWidget(self.ollama_browser)
        self.ollama_tab.setLayout(self.ollama_layout)
        self.tab_widget.addTab(self.ollama_tab, "Ollama")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.podman_status = self.create_status_indicator("Podman")
        self.ollama_status = self.create_status_indicator("Ollama")
        self.openwebui_status = self.create_status_indicator("Open-webUI")
        
        self.status_bar.addPermanentWidget(self.podman_status)
        self.status_bar.addPermanentWidget(self.ollama_status)
        self.status_bar.addPermanentWidget(self.openwebui_status)
        
        # Read config
        self.config = configparser.ConfigParser()
        self.config.read('cfg/config.ini')
        
        # Update status indicators
        self.update_status_indicators()
        
        # Set up a timer to periodically update status
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status_indicators)
        self.timer.start(5000)  # Update every 5 seconds

    def create_status_indicator(self, name):
        indicator = QWidget()
        indicator.setFixedSize(100, 30)
        layout = QVBoxLayout(indicator)
        label = QLabel(name)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        status_light = QWidget()
        status_light.setFixedSize(20, 20)
        status_light.setStyleSheet("background-color: gray; border-radius: 10px; margin: 5px;")
        layout.addWidget(status_light, alignment=Qt.AlignmentFlag.AlignCenter)
        return indicator

    def update_status_indicators(self):
        self.update_podman_status()
        self.update_container_status("ollama", self.ollama_status)
        self.update_container_status("openwebui", self.openwebui_status)

    def update_podman_status(self):
        try:
            subprocess.run(["podman", "info"], check=True, capture_output=True)
            self.set_status_color(self.podman_status, "green")
        except subprocess.CalledProcessError:
            self.set_status_color(self.podman_status, "red")

    def update_container_status(self, container_name, status_widget):
        try:
            result = subprocess.run(["podman", "inspect", "-f", "{{.State.Running}}", self.config['Containers'][container_name]], 
                                    check=True, capture_output=True, text=True)
            if result.stdout.strip() == "true":
                self.set_status_color(status_widget, "green")
            else:
                self.set_status_color(status_widget, "red")
        except subprocess.CalledProcessError:
            self.set_status_color(status_widget, "yellow")

    def set_status_color(self, widget, color):
        widget.findChild(QWidget).setStyleSheet(f"background-color: {color}; border-radius: 10px; margin: 5px;")

def main():
    print("Starting application...")
    app = QApplication(sys.argv)
    print("QApplication created")
    
    # Show splash screen
    splash = SplashScreen()
    print("Splash screen created")
    splash.show()
    print("Splash screen shown")
    
    # Simulate loading time
    start_time = time.time()
    while time.time() - start_time < 2:
        app.processEvents()
    print("Loading time simulated")
    
    # Create and show main window
    main_window = MainWindow()
    print("Main window created")
    main_window.show()
    print("Main window shown")
    
    # Close splash screen
    splash.finish(main_window)
    print("Splash screen finished")
    
    print("Entering main event loop")
    sys.exit(app.exec())

if __name__ == "__main__":
    main()