from datetime import datetime

node_name_base = "node"
log_end = ".log"
test_node_log = "test_node.log"

test_node_count = 20
node_timeout_limit = 20

measurement_log_file = "measurement_data.log"

calculated_metrics = "calculated_metrics.txt"

def get_datetime_from_line(line):
    time_part = line.split(': ')[0].strip()
    return datetime.strptime(time_part, '%Y-%m-%d %H:%M:%S.%f')


def get_node_from_line(line):
    return line.split(': ')[1]


def get_duration_from_line(line):
    duration_part = line.split(': ')[3].strip()
    return datetime.strptime(duration_part, '%H:%M:%S.%f')


def get_timestamp_and_node(line):
    timestamp = get_datetime_from_line(line)
    node = get_node_from_line(line)
    return timestamp, node


def get_found_all(log_file):
    with open(log_file) as f:
        for line in f:
            if "Found all nodes" in line:
                timestamp, node = get_timestamp_and_node(line)
                duration = get_duration_from_line(line)
                return timestamp, node, duration


def get_added_node_from_line(line):
    node = line.split("'")[1]
    return node


def get_added_data(line):
    timestamp, node = get_timestamp_and_node(line)
    added_node = get_added_node_from_line(line)
    return timestamp, node, added_node


def get_leaved_data(line):
    timestamp, node = get_timestamp_and_node(line)
    data_part = line.split(": ")[2].strip()
    leaved_node = data_part.replace("Peer ", "").replace(" timed out", "")
    return timestamp, node, leaved_node


def get_measurements_from_logs(node_count):
    measurement_data = {'found_all': [], 'node_found': [], 'node_left': []}

    timestamp, node, duration = get_found_all(test_node_log)
    data = {'timestamp': timestamp, 'node': node, 'duration': duration}
    measurement_data['found_all'].append(data)
    node_numbers = range(1, node_count + 1)

    for node_number in node_numbers:
        log_file = node_name_base + str(node_number) + log_end
        # print(log_file)
        with open(log_file, 'r') as log:
            for line in log:
                if not line.strip():
                    continue
                elif "Created logfile" in line:
                    continue
                elif line.startswith('<<<') or line.startswith('{'):
                    continue
                elif "Added" in line and "to peers" in line:
                    timestamp, node, added_node = get_added_data(line)
                    data = {'timestamp': timestamp, 'node': node, 'added_node': added_node}
                    measurement_data['node_found'].append(data)
                elif "Peer" in line and "timed out" in line:
                    timestamp, node, disappeared_node = get_leaved_data(line)
                    data = {'timestamp': timestamp, 'node': node, 'disappeared_node': disappeared_node}
                    measurement_data['node_left'].append(data)

    return measurement_data

def get_discovered_node_from_line(line):
	discovered_node = line.split(': ')[2]
	discovered_node = line.split("'")[1]
	return discovered_node

def get_all_discovered(line):
	node = get_node_from_line(line)
	data_part = line.split('duration: ')[1]
	duration = data_part.replace(')','')
	return node, duration

def get_data_from_measurement_log(log_file=measurement_log_file):
	measurement_log_data = {'discovery_started': [], 'discovered': [], 'all_discovered': [], 'shutdown': []}
	with open(log_file, 'r') as log:
		for line in log:
			if "Created" in line:
				continue
			elif "Discovery started" in line:
				timestamp, node = get_timestamp_and_node(line)
				data = {'timestamp': timestamp, 'node': node}
				measurement_log_data['discovery_started'].append(data)
			elif "Discovered" in line:
				timestamp, node = get_timestamp_and_node(line)
				discovered_node = get_discovered_node_from_line(line)
				data = {'timestamp': timestamp, 'node': node, 'discovered_node': discovered_node}
				measurement_log_data['discovered'].append(data)
			elif "All nodes discovered" in line:
				node, duration = get_all_discovered(line)
				data = {'node': node, 'duration': duration}
				measurement_log_data['all_discovered'].append(data)
			elif "Node shutdown" in line:
				timestamp, node = get_timestamp_and_node(line)
				data = {'timestamp': timestamp, 'node': node}
				measurement_log_data['shutdown'].append(data)
	return measurement_log_data


def calculate_leaved_discovered(logs_data, measurement_data):
	disappeared_times = []
	result = []
	for shutdown in measurement_data['shutdown']:
		node = shutdown['node']
		shutdown_time = shutdown['timestamp']
		#print(shutdown_time)
		disappeared_time_durations = []
		for node_left in logs_data['node_left']:
			#print(node.replace("'","").strip() + "/" + node_left['disappeared_node'].strip())
			#print(str(node_left['disappeared_node']) == str(node.replace("'","")))
			if str(node_left['disappeared_node']) == str(node.replace("'","")):
				disappeared_time = node_left['timestamp']
				#print(disappeared_time)
				duration = disappeared_time - shutdown_time				
				disappeared_times.append(duration)
		disappeared_time_min = min(disappeared_times)
		#print(disappeared_time_min)
		disappeared_time_max = max(disappeared_times)
		dt = {'disappeared_node': node, 'min': disappeared_time_min, 'max': disappeared_time_max}
		result.append(dt)
	return result

def calculate_metrics_from_data(logs_data, measurement_data):
	pass

def calculate_metrics(nodes_in_network):
	measurement_data_from_logs = get_measurements_from_logs(test_node_count)
    # print(measurement_data_from_logs)
    # print("\n\n")
	measurement_log_data = get_data_from_measurement_log()
    #print(measurement_log_data['all_discovered'])

	with open(calculated_metrics, 'a') as output:
		# Test case.
		text = "----{0} node network + test node----\n".format(nodes_in_network)
		output.write(text)
		# Found all discoveries.
		text = "New node discovered nodes in network:\n"
		output.write(text)
		for data in measurement_log_data['all_discovered']:    		
			text = "Node '{0}' discovered all in {1}\n".format(data['node'], data['duration'])
			output.write(text)

		# Node disappearing discoveries.
		node_disappeared_calcs = calculate_leaved_discovered(measurement_data_from_logs, measurement_log_data)
		text = "\nNode disappearing discovery times ({0} second timeout limit):\n".format(node_timeout_limit)
		output.write(text)
		for data in node_disappeared_calcs:
			text = "{0}: min: {1}, max: {2}\n".format(data['disappeared_node'], str(data['min']), str(data['max']))
			output.write(text)
		output.write("-----------------------------------\n\n")

def main():
    calculate_metrics(test_node_count)

if __name__ == '__main__':
    main()