#!/usr/bin/env python3
import os
import sys
import subprocess
import tkinter as tk
from tkinter import ttk
from threading import Thread
import time

class UpdateDialog:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Plane Simulator Updater")
        
        # Set window size and position it in the center
        window_width = 400
        window_height = 150
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Make window float on top
        self.root.attributes('-topmost', True)
        
        # Configure grid
        self.root.grid_columnconfigure(0, weight=1)
        for i in range(4):
            self.root.grid_rowconfigure(i, weight=1)
        
        # Status label
        self.status_label = ttk.Label(self.root, text="Checking for updates...", font=('Helvetica', 12))
        self.status_label.grid(row=0, column=0, pady=10, padx=20)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.grid(row=1, column=0, sticky='ew', padx=20)
        
        # Details label
        self.details_label = ttk.Label(self.root, text="", font=('Helvetica', 10))
        self.details_label.grid(row=2, column=0, pady=5, padx=20)
        
        self.progress.start()
        
        # Start update check in separate thread
        self.update_thread = Thread(target=self.check_for_updates)
        self.update_thread.start()
        
    def run_command(self, cmd, cwd=None):
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=cwd
            )
            stdout, stderr = process.communicate()
            return process.returncode, stdout, stderr
        except Exception as e:
            return 1, "", str(e)
    
    def check_for_updates(self):
        try:
            # Get the Resources directory path
            resources_dir = os.path.dirname(os.path.abspath(__file__))
            repo_dir = os.path.join(resources_dir, "repo")
            
            self.details_label.config(text="Initializing...")
            
            # If repo doesn't exist, clone it
            if not os.path.exists(repo_dir):
                self.status_label.config(text="First time setup")
                self.details_label.config(text="Cloning repository...")
                
                returncode, _, stderr = self.run_command(
                    ["git", "clone", "https://github.com/BismuthLm/plane-simulator.git", repo_dir]
                )
                if returncode != 0:
                    raise Exception(f"Failed to clone repository: {stderr}")
                
                # Copy files to Resources directory
                for file in ['plane_simulator.py', 'requirements.txt']:
                    src = os.path.join(repo_dir, file)
                    dst = os.path.join(resources_dir, file)
                    if os.path.exists(src):
                        with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                            fdst.write(fsrc.read())
            
            else:
                # Check for updates
                self.details_label.config(text="Checking remote repository...")
                
                # Fetch latest changes
                returncode, _, stderr = self.run_command(
                    ["git", "fetch", "origin", "main"],
                    cwd=repo_dir
                )
                if returncode != 0:
                    raise Exception(f"Failed to fetch updates: {stderr}")
                
                # Get local and remote hashes
                returncode, local_hash, _ = self.run_command(
                    ["git", "rev-parse", "HEAD"],
                    cwd=repo_dir
                )
                returncode, remote_hash, _ = self.run_command(
                    ["git", "rev-parse", "origin/main"],
                    cwd=repo_dir
                )
                
                if local_hash.strip() != remote_hash.strip():
                    self.status_label.config(text="Update available!")
                    self.details_label.config(text="Downloading updates...")
                    
                    # Pull changes
                    returncode, _, stderr = self.run_command(
                        ["git", "pull", "origin", "main"],
                        cwd=repo_dir
                    )
                    if returncode != 0:
                        raise Exception(f"Failed to pull updates: {stderr}")
                    
                    # Copy updated files
                    self.details_label.config(text="Installing updates...")
                    for file in ['plane_simulator.py', 'requirements.txt']:
                        src = os.path.join(repo_dir, file)
                        dst = os.path.join(resources_dir, file)
                        if os.path.exists(src):
                            with open(src, 'rb') as fsrc, open(dst, 'wb') as fdst:
                                fdst.write(fsrc.read())
                    
                    # Update dependencies
                    venv_dir = os.path.join(resources_dir, "venv")
                    if os.path.exists(os.path.join(venv_dir, "bin", "activate")):
                        self.details_label.config(text="Updating dependencies...")
                        returncode, _, stderr = self.run_command(
                            [os.path.join(venv_dir, "bin", "pip"), "install", "-r", "requirements.txt"],
                            cwd=resources_dir
                        )
                        if returncode != 0:
                            raise Exception(f"Failed to update dependencies: {stderr}")
            
            self.status_label.config(text="Starting game...")
            self.details_label.config(text="")
            time.sleep(1)  # Show "Starting game..." briefly
            self.root.quit()
            
        except Exception as e:
            self.status_label.config(text="Error")
            self.details_label.config(text=str(e))
            self.progress.stop()
            # Add a close button when there's an error
            ttk.Button(self.root, text="Close", command=self.root.quit).grid(row=3, column=0, pady=10)
            return

if __name__ == "__main__":
    dialog = UpdateDialog()
    dialog.root.mainloop()
