import psutil
import time

def cpuUsage():
	cpuTime = psutil.cpu_times_percent(interval=2)
	userUsage = cpuTime.user + cpuTime.nice + cpuTime.guest + cpuTime.guest_nice
	systemUsage = cpuTime.system + cpuTime.iowait + cpuTime.irq + cpuTime.softirq + cpuTime.steal
	cpuUsages = {"User": userUsage, "System": systemUsage, "Idle": cpuTime.idle}
	return cpuUsages

def memUsage():
	memUsages = psutil.virtual_memory()
	return {"available": memUsages.available, "total": memUsages.total, "usage": memUsages.percent}

def disksUsage():
	interval = 4
	before = psutil.disk_io_counters(perdisk=True)
	time.sleep(interval)
	after = psutil.disk_io_counters(perdisk=True)

	disksUsages = {}

	for disk in before.keys():
		if "loop" in disk:
			continue
		read_speed = (after[disk].read_bytes - before[disk].read_bytes) / interval  # in bytes per second
		write_speed = (after[disk].write_bytes - before[disk].write_bytes) / interval  # in bytes per second
		disksUsages[disk] = {
			"read_speed": read_speed,
			"write_speed": write_speed,
			"mounted": False,
		}

	# print(psutil.disk_io_counters(perdisk=True)["nvme0n1p5"].write_bytes)
	parts = psutil.disk_partitions()
	for part in parts:
		mtpt = part.mountpoint
		if mtpt == "/boot/efi":
			continue
		usage = psutil.disk_usage(mtpt)
		disk = part.device.split("/")[-1]
		disksUsages[disk]["mountpoint"] = mtpt
		disksUsages[disk]["free"] = usage.free
		disksUsages[disk]["total"] = usage.total
		disksUsages[disk]["usage"] = usage.percent
		disksUsages[disk]["mounted"] = True

	diskList = []
	for key, value in disksUsages.items():
		value["name"] = key
		diskList.append(value)

	return diskList

def netUsage():
	interval = 2
	before = psutil.net_io_counters(pernic=True)
	time.sleep(interval)
	after = psutil.net_io_counters(pernic=True)

	netUsages = {}

	for nic in before.keys():
		if nic == "lo":
			continue
		sent_speed = (after[nic].bytes_sent - before[nic].bytes_sent) / interval  # in bytes per second
		recv_speed = (after[nic].bytes_recv - before[nic].bytes_recv) / interval  # in bytes per second

		netUsages[nic] = {
			"sent_speed": sent_speed,
			"recv_speed": recv_speed
		}

	netList = []
	for key, value in netUsages.items():
		value["name"] = key
		netList.append(value)
	return netList

def system():
	cpuUsages = cpuUsage()
	memUsages = memUsage()
	disksUsages = disksUsage()
	netUsages = netUsage()
	return {"cpu": cpuUsages, "mem": memUsages, "disks": disksUsages, "network": netUsages}

def processes(WhiteList=[]):
	# cpuTime = psutil.cpu_times()
	# totalCpuTime = cpuTime.user + cpuTime.nice + cpuTime.guest + cpuTime.guest_nice + cpuTime.system + cpuTime.iowait + cpuTime.irq + cpuTime.softirq + cpuTime.steal + cpuTime.idle
	cpu_count = psutil.cpu_count(logical=True)

	allProcs = [p for p in psutil.process_iter(['name', 'pid', 'username', 'cpu_percent', 'memory_full_info'])]
	procUsage = {"system":{"cpu":0, 'mem': 0}}
	# for name in WhiteList:
	# 	procUsage[name] = {"cpu":0, 'mem': 0}

	system_memory = psutil.virtual_memory().total

	for proc in allProcs:
		try:
			if proc.name() in WhiteList or WhiteList == []:
				if proc.name() not in procUsage.keys():
					procUsage[proc.name()] = {"cpu":0, 'mem': 0}
				try:
					procUsage[proc.name()]["cpu"] += proc.cpu_percent() / cpu_count
					procUsage[proc.name()]["mem"] += proc.memory_full_info().rss
				except KeyError:
					pass
			else:
				procUsage["system"]["cpu"] += proc.cpu_percent() / cpu_count
				procUsage["system"]["mem"] += proc.memory_full_info().rss
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
			pass

	return procUsage

if __name__ == '__main__':
	print(system())
	# print(processes(["vivaldi-bin"]))
	# print(processes())