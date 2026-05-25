import subprocess
import re
import psutil
import os
import json
from datetime import datetime

class CPUMonitor:
    def __init__(self):
        self.log_file = os.path.expanduser('~/.cpu-web-tuner/logs/cpu_data.jsonl')
    
    def get_temperatures(self):
        try:
            output = subprocess.check_output(['sensors'], text=True)
            temps = {}
            for line in output.split('\n'):
                if 'Core' in line or 'Tctl' in line:
                    match = re.search(r'\+(\d+\.\d+)', line)
                    if match:
                        core_name = line.split(':')[0].strip()
                        temps[core_name] = float(match.group(1))
            return temps
        except:
            return {'error': 'sensors not available'}
    
    def get_frequencies(self):
        freqs = {}
        for i, cpu in enumerate(psutil.cpu_freq(percpu=True)):
            freqs[f'CPU{i}'] = round(cpu.current / 1000, 2)  # MHz to GHz
        return freqs
    
    def get_governor(self):
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor', 'r') as f:
                return f.read().strip()
        except:
            return 'unknown'
    
    def set_governor(self, governor):
        try:
            for cpu in range(psutil.cpu_count()):
                with open(f'/sys/devices/system/cpu/cpu{cpu}/cpufreq/scaling_governor', 'w') as f:
                    f.write(governor)
            return True
        except Exception as e:
            return str(e)
    
    def get_cpu_usage(self):
        return psutil.cpu_percent(percpu=True)
    
    def get_memory_info(self):
        mem = psutil.virtual_memory()
        return {
            'total': round(mem.total / (1024**3), 2),
            'used': round(mem.used / (1024**3), 2),
            'percent': mem.percent
        }
    
    def get_available_governors(self):
        try:
            with open('/sys/devices/system/cpu/cpu0/cpufreq/scaling_available_governors', 'r') as f:
                return f.read().strip().split()
        except:
            return ['performance', 'powersave', 'ondemand', 'conservative', 'schedutil']
    
    def log_data(self):
        data = {
            'timestamp': datetime.now().isoformat(),
            'temperatures': self.get_temperatures(),
            'frequencies': self.get_frequencies(),
            'cpu_usage': self.get_cpu_usage(),
            'memory': self.get_memory_info()
        }
        with open(self.log_file, 'a') as f:
            f.write(json.dumps(data) + '\n')
        return data
    
    def get_stats(self, hours=24):
        if not os.path.exists(self.log_file):
            return {}
        
        data = []
        with open(self.log_file, 'r') as f:
            for line in f:
                data.append(json.loads(line))
        
        if not data:
            return {}
        
        temps = [d['temperatures'].get('Core 0', 0) for d in data if 'Core 0' in d['temperatures']]
        
        return {
            'max_temp': max(temps) if temps else 0,
            'min_temp': min(temps) if temps else 0,
            'avg_temp': sum(temps) / len(temps) if temps else 0,
            'total_records': len(data)
        }