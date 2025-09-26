import os, platform, socket, psutil, netifaces, cpuinfo, time
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.panel import Panel
from rich.align import Align



kb = float(1024)
mb = float(kb ** 2)
gb = float(kb ** 3)


# Use attribute names for better compatibility
vmem = psutil.virtual_memory()
memTotal = int(vmem.total/gb)
memFree = int(vmem.available/gb)
memUsed = int(vmem.used/gb)
memPercent = int(memUsed/memTotal*100) if memTotal else 0

# Use current drive for Windows
if os.name == 'nt':
    disk_path = os.environ.get('SystemDrive', 'C:') + '\\'
else:
    disk_path = '/'
disk = psutil.disk_usage(disk_path)
storageTotal = int(disk.total/gb)
storageUsed = int(disk.used/gb)
storageFree = int(disk.free/gb)
storagePercent = int(storageUsed/storageTotal*100) if storageTotal else 0

info = cpuinfo.get_cpu_info().get('brand_raw', 'Unknown')

def service():
    pidTotal = len(psutil.pids())
    return pidTotal


def load_avg():
    if hasattr(os, 'getloadavg'):
        la = os.getloadavg()
        return [round(la[0],2), round(la[1],2), round(la[2],2)]
    else:
        return ["N/A", "N/A", "N/A"]

def system():
    core = os.cpu_count()
    host = socket.gethostname()
    return {
        "Hostname": host,
        "System": f"{platform.system()} {platform.machine()}",
        "Kernel": platform.release(),
        "Compiler": platform.python_compiler(),
        "CPU": f"{info} ({core} cores)",
        "Memory": f"{memTotal} GiB",
        "Disk": f"{storageTotal} GiB"
    }


def cpu():
    cpu_percent = psutil.cpu_percent(interval=0.5)
    return cpu_percent

def memory():
    return {
        "RAM Used": f"{memUsed} GiB / {memTotal} GiB ({memPercent}%)",
        "Disk Used": f"{storageUsed} GiB / {storageTotal} GiB ({storagePercent}%)"
    }


def network():
    gateways = netifaces.gateways()
    active = None
    if 'default' in gateways and netifaces.AF_INET in gateways['default']:
        active = gateways['default'][netifaces.AF_INET][1]
    else:
        active = 'Unknown'
    net = psutil.net_io_counters(pernic=True)
    if active in net:
        stats = net[active]
    else:
        stats = psutil.net_io_counters(pernic=False)
    psend = round(stats.bytes_sent/kb, 2)
    precv = round(stats.bytes_recv/kb, 2)
    return {
        "Active Interface": active,
        "Bytes Sent": f"{psend} KiB",
        "Bytes Received": f"{precv} KiB"
    }



def dashboard():
    console = Console()
    with Live(refresh_per_second=1, console=console) as live:
        while True:
            sysinfo = system()
            cpu_percent = cpu()
            meminfo = memory()
            netinfo = network()
            load = load_avg()
            procs = service()

            sys_table = Table(title="System Info", show_header=False)
            for k, v in sysinfo.items():
                sys_table.add_row(k, str(v))

            cpu_table = Table(title="CPU Usage", show_header=False)
            cpu_table.add_row("CPU Usage", f"{cpu_percent} %")

            mem_table = Table(title="Memory & Disk", show_header=False)
            for k, v in meminfo.items():
                mem_table.add_row(k, v)

            net_table = Table(title="Network", show_header=False)
            for k, v in netinfo.items():
                net_table.add_row(k, v)

            load_table = Table(title="Load Average", show_header=False)
            load_table.add_row("1 min", str(load[0]))
            load_table.add_row("5 min", str(load[1]))
            load_table.add_row("15 min", str(load[2]))

            procs_table = Table(title="Processes", show_header=False)
            procs_table.add_row("Running Processes", str(procs))

            # Layout
            grid = Table.grid(expand=True)
            grid.add_row(
                Panel(sys_table, border_style="cyan"),
                Panel(cpu_table, border_style="magenta"),
                Panel(mem_table, border_style="green")
            )
            grid.add_row(
                Panel(net_table, border_style="yellow"),
                Panel(load_table, border_style="blue"),
                Panel(procs_table, border_style="red")
            )

            live.update(Align.center(grid))
            time.sleep(1)

if __name__ == "__main__":
    dashboard()