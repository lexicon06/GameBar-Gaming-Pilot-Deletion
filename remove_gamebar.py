#!/usr/bin/env python3
"""
Xbox Game Bar & Gaming Overlay Complete Removal Script
Run as Administrator for full effect
"""

import os
import sys
import ctypes
import subprocess
import shutil
from pathlib import Path
import winreg
import time

def is_admin():
    """Check if script is running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_powershell(command):
    """Execute PowerShell command and return output"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            shell=True,
            timeout=30
        )
        return result.stdout, result.stderr, result.returncode
    except Exception as e:
        return "", str(e), 1

def remove_gamebar_packages():
    """Remove all Xbox Game Bar related packages"""
    print("[1/8] Removing Xbox Game Bar packages...")
    
    packages = [
        "Microsoft.XboxGamingOverlay",
        "Microsoft.XboxGameOverlay",
        "Microsoft.XboxSpeechToTextOverlay",
        "Microsoft.XboxIdentityProvider",
        "Microsoft.Xbox.TCUI",
        "Microsoft.XboxApp",
        "Microsoft.GamingApp",
        "Microsoft.GamingServices"
    ]
    
    for package in packages:
        print(f"  Removing {package}...")
        cmd = f"Get-AppxPackage *{package}* | Remove-AppxPackage -AllUsers -ErrorAction SilentlyContinue"
        stdout, stderr, code = run_powershell(cmd)
        if "not installed" not in stderr and "not found" not in stderr:
            print(f"    ✓ Removed {package}")
        time.sleep(0.5)

def disable_services():
    """Disable all Xbox related services"""
    print("[2/8] Disabling Xbox services...")
    
    services = [
        "XblGameSave",
        "XblAuthManager",
        "XboxNetApiSvc",
        "XboxGipSvc",
        "XboxGamestreamingSvc"
    ]
    
    for service in services:
        try:
            # Stop service if running
            subprocess.run(f"sc stop {service}", shell=True, capture_output=True, text=True)
            # Disable service
            subprocess.run(f"sc config {service} start= disabled", shell=True, capture_output=True, text=True)
            print(f"    ✓ Disabled {service}")
        except:
            pass

def registry_cleanup():
    """Clean registry entries for Game Bar"""
    print("[3/8] Cleaning registry entries...")
    
    registry_entries = [
        # Game DVR settings
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\GameDVR", [
            ("AppCaptureEnabled", 0),
            ("AudioCaptureEnabled", 0),
            ("HistoricalCaptureEnabled", 0),
            ("CursorCaptureEnabled", 0),
            ("CustomVideoEncodingProfile", 0),
            ("VideoEncodingResolution", 0),
            ("VideoEncodingBitrate", 0),
            ("VideoEncodingFramerate", 0)
        ]),
        
        # Game config store
        (winreg.HKEY_CURRENT_USER, r"System\GameConfigStore", [
            ("GameDVR_Enabled", 0),
            ("GameDVR_FSEBehaviorMode", 0),
            ("GameDVR_HonorUserFSEBehaviorMode", 0),
            ("GameDVR_DXGIHonorFSEWindowsCompatible", 0),
            ("GameDVR_EFSEFeatureFlags", 0),
            ("Win32_AutoGameModeEnabled", 0),
            ("Win32_GameModeRelatedProcessesOptedIn", 0)
        ]),
        
        # Game bar policies
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Policies\Microsoft\Windows\GameDVR", [
            ("AllowGameDVR", 0)
        ]),
        
        # Xbox identity
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\XboxLive", [
            ("DisableGameBar", 1)
        ])
    ]
    
    for hive, key_path, values in registry_entries:
        try:
            # Open or create key
            try:
                if hive == winreg.HKEY_CURRENT_USER:
                    key = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)
                else:
                    key = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_WRITE)
            except:
                continue
            
            # Set values
            for value_name, value_data in values:
                winreg.SetValueEx(key, value_name, 0, winreg.REG_DWORD, value_data)
            
            winreg.CloseKey(key)
        except Exception as e:
            print(f"    ⚠ Could not set {key_path}: {e}")
    
    print("    ✓ Registry cleaned")

def delete_cache_folders():
    """Delete Game Bar cache and data folders"""
    print("[4/8] Deleting cache and data folders...")
    
    cache_folders = [
        os.path.expandvars(r"%LocalAppData%\Microsoft\XboxGameCallableUI"),
        os.path.expandvars(r"%LocalAppData%\Microsoft\XboxLive"),
        os.path.expandvars(r"%LocalAppData%\Packages\Microsoft.XboxGamingOverlay_8wekyb3d8bbwe"),
        os.path.expandvars(r"%LocalAppData%\Packages\Microsoft.XboxGameOverlay_8wekyb3d8bbwe"),
        os.path.expandvars(r"%AppData%\Microsoft\Windows\GameBar"),
        os.path.expandvars(r"%ProgramData%\Microsoft\Windows\GameBar")
    ]
    
    deleted_count = 0
    for folder in cache_folders:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder, ignore_errors=True)
                deleted_count += 1
            except:
                pass
    
    print(f"    ✓ Deleted {deleted_count} cache folders")

def disable_task_scheduler():
    """Disable Game Bar related scheduled tasks"""
    print("[5/8] Disabling scheduled tasks...")
    
    tasks = [
        r"\Microsoft\XblGameSave\XblGameSaveTask",
        r"\Microsoft\XblGameSave\XblGameSaveTaskLogon",
        r"\Microsoft\Windows\GameSave\GameSaveTask",
        r"\Microsoft\Windows\GameSave\GameSaveTaskLogon"
    ]
    
    for task in tasks:
        try:
            subprocess.run(f'schtasks /Change /TN "{task}" /DISABLE', 
                         shell=True, capture_output=True, text=True)
        except:
            pass
    
    print("    ✓ Scheduled tasks disabled")

def modify_hosts_file():
    """Block Xbox domains in hosts file"""
    print("[6/8] Blocking Xbox domains...")
    
    hosts_path = r"C:\Windows\System32\drivers\etc\hosts"
    xbox_domains = [
        "0.0.0.0 gaming.xbox.com",
        "0.0.0.0 xbox.com",
        "0.0.0.0 xboxlive.com",
        "0.0.0.0 microsoft.com/xbox",
        "127.0.0.1 Microsoft.XboxGamingOverlay",
        "127.0.0.1 Microsoft.XboxGameOverlay",
        "127.0.0.1 xbox.gamebar.exe",
        "0.0.0.0 xbox.ipv6.microsoft.com"
    ]
    
    try:
        # Read current hosts
        with open(hosts_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove existing Xbox entries
        lines = content.split('\n')
        filtered_lines = []
        for line in lines:
            if not any(domain in line.lower() for domain in 
                       ['gaming.xbox.com', 'xbox.com', 'xboxlive.com', 'xboxgamingoverlay']):
                filtered_lines.append(line)
        
        # Add new entries if not already present
        for domain in xbox_domains:
            if domain not in content:
                filtered_lines.append(domain)
        
        # Write back
        with open(hosts_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(filtered_lines))
        
        print("    ✓ Hosts file updated")
    except Exception as e:
        print(f"    ⚠ Could not modify hosts file: {e}")

def create_firewall_rules():
    """Create firewall rules to block Game Bar"""
    print("[7/8] Creating firewall rules...")
    
    # Block GameBar executables
    firewall_cmds = [
        'netsh advfirewall firewall add rule name="Block GameBar" dir=out action=block program="C:\\Program Files\\WindowsApps\\*\\XboxGameOverlay.exe" enable=yes',
        'netsh advfirewall firewall add rule name="Block GameBar System" dir=out action=block program="C:\\Windows\\SystemApps\\*GameBar*\\GameBar.exe" enable=yes',
        'netsh advfirewall firewall add rule name="Block GameBar Presence" dir=out action=block program="C:\\Windows\\System32\\GameBarPresenceWriter.exe" enable=yes'
    ]
    
    for cmd in firewall_cmds:
        try:
            subprocess.run(cmd, shell=True, capture_output=True, text=True)
        except:
            pass
    
    print("    ✓ Firewall rules created")

def final_touches():
    """Final cleanup and settings"""
    print("[8/8] Applying final settings...")
    
    # Disable via Windows Settings if possible
    try:
        # Disable Game Bar via registry commands (using raw strings to avoid escape issues)
        reg_commands = [
            r'reg add "HKCU\Software\Microsoft\GameBar" /v "ShowStartupPanel" /t REG_DWORD /d 0 /f',
            r'reg add "HKCU\Software\Microsoft\GameBar" /v "AutoGameModeEnabled" /t REG_DWORD /d 0 /f',
            r'reg add "HKCU\Software\Microsoft\GameBar" /v "ShowTips" /t REG_DWORD /d 0 /f',
            r'reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f',
            r'reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f'
        ]
        
        for cmd in reg_commands:
            subprocess.run(cmd, shell=True, capture_output=True, text=True)
    except:
        pass
    
    # Kill any remaining GameBar processes
    processes = ["GameBar.exe", "GameBarFT.exe", "XboxGameOverlay.exe", "GamingOverlay.exe"]
    for proc in processes:
        try:
            subprocess.run(f'taskkill /f /im {proc} 2>nul', shell=True)
        except:
            pass
    
    print("    ✓ Final settings applied")

def create_prevention_script():
    """Create a startup script to prevent Game Bar from re-enabling"""
    print("\n[+] Creating prevention script...")
    
    script_content = r'''@echo off
REM Game Bar Prevention Script - Run at startup
REM Place in Startup folder: %AppData%\Microsoft\Windows\Start Menu\Programs\Startup
REM Or run manually when needed

:loop
REM Kill Game Bar processes
taskkill /f /im GameBar.exe 2>nul
taskkill /f /im GameBarFT.exe 2>nul
taskkill /f /im XboxGameOverlay.exe 2>nul
taskkill /f /im GamingOverlay.exe 2>nul

REM Disable services
sc config XblGameSave start= disabled >nul 2>&1
sc config XblAuthManager start= disabled >nul 2>&1

REM Update registry
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v "AppCaptureEnabled" /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v "GameDVR_Enabled" /t REG_DWORD /d 0 /f >nul 2>&1

REM Wait 30 seconds
timeout /t 30 /nobreak >nul
goto loop
'''
    
    # Save to current directory (where script is run from)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(script_dir, "PreventGameBar.bat")
    
    with open(script_path, "w", encoding='utf-8') as f:
        f.write(script_content)
    
    print(f"    ✓ Prevention script created: {script_path}")
    print("    Run this script at startup to prevent Game Bar from re-enabling")
    
    # Also offer to create in Startup folder
    try:
        startup_folder = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        startup_path = os.path.join(startup_folder, "PreventGameBar.bat")
        shutil.copy2(script_path, startup_path)
        print(f"    ✓ Also copied to Startup folder: {startup_path}")
    except:
        print("    ⚠ Could not copy to Startup folder (run as admin might help)")

def main():
    """Main function"""
    print("=" * 60)
    print("    Xbox Game Bar & Gaming Overlay Complete Removal")
    print("    Run as Administrator for full effect")
    print("=" * 60)
    
    # Check for admin rights
    if not is_admin():
        print("\n[!] ERROR: This script requires Administrator privileges!")
        print("[!] Please right-click and 'Run as administrator'")
        input("\nPress Enter to exit...")
        sys.exit(1)
    
    # Confirm
    print("\n[!] WARNING: This will completely disable Xbox Game Bar")
    print("[!] Some Windows features may stop working")
    print("[!] Game recording, screenshots via Game Bar will be disabled\n")
    
    response = input("Continue? (y/N): ").strip().lower()
    if response != 'y':
        print("Operation cancelled.")
        return
    
    try:
        # Execute all removal steps
        remove_gamebar_packages()
        disable_services()
        registry_cleanup()
        delete_cache_folders()
        disable_task_scheduler()
        modify_hosts_file()
        create_firewall_rules()
        final_touches()
        
        # Create prevention script
        create_prevention_script()
        
        print("\n" + "=" * 60)
        print("    COMPLETE! Game Bar has been disabled")
        print("=" * 60)
        print("\n[!] IMPORTANT: Restart your computer for all changes to take effect")
        print("[!] Some games may still show prompts - check individual game settings")
        print("[!] Windows Updates may reinstall components - run script again if needed")
        
        restart = input("\nRestart now? (y/N): ").strip().lower()
        if restart == 'y':
            subprocess.run("shutdown /r /t 5", shell=True)
            print("Restarting in 5 seconds...")
        
    except Exception as e:
        print(f"\n[!] Error occurred: {e}")
        print("[!] Some operations may have failed")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
