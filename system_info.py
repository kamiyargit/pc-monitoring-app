import psutil
import platform
import time

def get_system_info():
    """Get system information including CPU, RAM, OS and uptime."""
    
    # CPU Info
    cpu_count = psutil.cpu_count(logical=True)
    cpu_freq = psutil.cpu_freq()
    cpu_model = ""
    
    try:
        # Try to get CPU model from system info
        cpu_model = platform.processor() or platform.machine()
    except:
        cpu_model = "Unknown"
    
    # Memory Info
    memory = psutil.virtual_memory()
    total_ram = memory.total
    available_ram = memory.available
    used_ram = memory.used
    ram_percent = memory.percent
    
    # OS Info
    os_name = platform.system()
    os_version = platform.release()
    
    # Uptime
    boot_time = psutil.boot_time()
    current_time = time.time()
    uptime_seconds = current_time - boot_time
    uptime_days = int(uptime_seconds // 86400)
    uptime_hours = int((uptime_seconds % 86400) // 3600)
    uptime_minutes = int((uptime_seconds % 3600) // 60)
    
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=1)
    
    return {
        'cpu_model': cpu_model,
        'cpu_count': cpu_count,
        'cpu_freq': cpu_freq,
        'cpu_percent': cpu_percent,
        'total_ram': total_ram,
        'available_ram': available_ram,
        'used_ram': used_ram,
        'ram_percent': ram_percent,
        'os_name': os_name,
        'os_version': os_version,
        'uptime_days': uptime_days,
        'uptime_hours': uptime_hours,
        'uptime_minutes': uptime_minutes
    }

def format_bytes(bytes_value):
    """Convert bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} PB"

def get_formatted_system_info():
    """Get formatted system information string."""
    info = get_system_info()
    
    formatted = (
        f"CPU: {info['cpu_model']} ({info['cpu_count']} cores)\n"
        f"CPU Usage: {info['cpu_percent']:.1f}%\n"
        f"RAM: {format_bytes(info['used_ram'])} / {format_bytes(info['total_ram'])} ({info['ram_percent']:.1f}% used)\n"
        f"OS: {info['os_name']} {info['os_version']}\n"
        f"Uptime: {info['uptime_days']}d {info['uptime_hours']}h {info['uptime_minutes']}m"
    )
    
    return formatted