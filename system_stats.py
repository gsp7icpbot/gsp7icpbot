##system_stats

import subprocess
import psutil

def get_cpu_temp():
    try:
        with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
            temp_str = f.readline()
            return round(float(temp_str) / 1000, 2)
    except Exception as e:
        return f"Error: {e}"

def get_power_status():
    try:
        result = subprocess.run(['vcgencmd', 'get_throttled'], capture_output=True, text=True)
        if result.returncode == 0:
            hex_val = result.stdout.strip().split('=')[1]
            status = int(hex_val, 16)
            if status == 0:
                return "⚡ Power: ✅Normal"
            msg = "⚠️ Power Issue Detected: "
            if status & 0x1:
                msg += "Under-voltage detected. "
            if status & 0x2:
                msg += "Arm frequency capped. "
            if status & 0x4:
                msg += "Currently throttled. "
            if status & 0x8:
                msg += "Soft temperature limit active. "
            return msg
        else:
            return "Power status: unknown"
    except Exception as e:
        return f"Error: {e}"
        
def get_cpu_usage():
    # Returns CPU usage percent (over all cores)
    return psutil.cpu_percent(interval=1)

def get_ram_usage():
    mem = psutil.virtual_memory()
    return mem.percent  # percentage of RAM used
