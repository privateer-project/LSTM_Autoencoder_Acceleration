import sys
import subprocess
import time

class power_scraper:
    def __init__(self, device_id) -> None: 
        self.device_id = device_id
        self.command = f'xbutil examine -d {device_id} --r electrical'

    def get_power(self):
        try:
            if(sys.version_info >= (3, 7)):
                result = subprocess.run(self.command, check=True, capture_output=True, universal_newlines=True, shell=True)
            else:
                result = subprocess.run(self.command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, shell=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        data = self.parse_power_data(result.stdout)
        data['time'] = time.time()
        return data
    
    def parse_power_data(self, output):
        lines = output.split('\n')
        data = {}
        power_rails = {}
        data['Max Power'] = int(lines[5].split(':')[1].strip().split()[0])
        data['Power'] = float(lines[6].split(':')[1].strip().split()[0])
        data['Power Warning'] = lines[7].split(':')[1].strip()
        for index, line in enumerate(lines):
            if(index > 10 and line.strip() != ''):
                name = line.split(':')[0].strip()
                voltage_current = line.split(':')[1].strip().split('  ')
                temp_dir = {'Voltage': float(voltage_current[0].strip().split()[0])}
                if(len(voltage_current) > 1):
                    temp_dir['Current'] = float(voltage_current[1].strip().split()[0])
                power_rails[name] = temp_dir
        data['Power Rails'] = power_rails
        return data