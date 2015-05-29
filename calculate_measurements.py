node_name_base = "node"
log_end = ".log"

node_count = 10

def main():
	node_numbers = range(1, node_count+1)
	for node_number in node_numbers:
		log_file = node_name_base + str(node_number) + log_end
		with open(log_file, 'r'):
		 



if __name__ == '__main__':
	main()