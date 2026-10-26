import subprocess
import os

gcloud_bin = "/usr/bin/gcloud"
project = "sym-onprem-gar"
location = "us-east4"
destination_path = "./"
RED = "\033[38;2;255;0;0m"
ORANGE = "\033[38;2;255;165;0m"
BLUE = "\033[38;2;0;155;255m"
GREEN = "\033[38;2;0;255;0m"
YELLOW = "\033[38;2;255;255;0m"
RESET = "\033[0m"

menu = ["list_repos"]
selected_repo = None

## Function
##  Main function that runs the program and handles user input and menu navigation.
def main():
	global selected_repo

	while True:
		action = getCurrentMenuLocation()
		list_repos = []
		filtered_repos = []
		list_files = []
		filtered_files = []
		selected_download = None

		if action == "list_repos":
			print("==============================")
			print(f"Building the repo list for the {ORANGE}{project}{RESET} project in the {ORANGE}{location}{RESET} location\n")

			## Query the GAR for the list of repositories and store results
			list_repos = query_gar(action, None, None)
			if not list_repos:
				continue

			## Filter the results to remove any repositories with the format "DOCKER" and store the filtered results
			filtered_repos = filter_results(list_repos, action)
			if not filtered_repos:
				continue

			## Print the list of filtered repositories
			print_list(filtered_repos, action)

			## Get input from the user to select a repository or exit the program
			selection = input(f"Repo {BLUE}#{RESET} or {BLUE}'q'{RESET} to quit: ")

			## Exit the program if the user selects 'q' or 'Q'
			if(selection == "q" or selection == "Q"):
				print(f" Exiting the program")
				exit(0)

			## Validate the user input and store the selected repository. The selected repository will be used in
			#   subsequent runs of the loop.
			try:
				num_selection = int(selection)
				if num_selection < 1:
					raise IndexError
				selected_repo = filtered_repos[int(num_selection) - 1][0]
			except (ValueError, IndexError):
				print(f" {RED}! Selected an invalid number{RESET}")
				selected_repo = None
				continue

			## Add the 'list_files' action to the menu list to allow the user to list files in the selected repository
			addToMenu("list_files")

		if action == "list_files":
			print("==============================")
			print(f"Building file list for the {GREEN}{selected_repo}{RESET} repo\n")

			## Query the GAR for the list of files in the selected repository and store results
			list_files = query_gar(action, selected_repo, None)
			if not list_files:
				continue

			## Filter the results to remove any files that start with "sha256:" and store the filtered results
			filtered_files = filter_results(list_files, action)
			if not filtered_files:
				continue

			## Print the list of filtered files
			print_list(filtered_files, action)

			## Get input from the user to select a repository
			selection = input(f"File {BLUE}#{RESET}, {BLUE}'b'{RESET} to go back, or {BLUE}'q'{RESET} to quit: ")
		
			## Exit the program if the user selects 'q' or 'Q'
			if selection == "q" or selection == "Q":
				print(f" Exiting the program")
				exit(0)

			## Go back to the previous menu if the user selects 'b' or 'B'
			if selection == "b" or selection == "B":
				removeFromMenu()
				continue

			## Validate the user input and print the selected repository
			try:
				num_selection = int(selection)
				if num_selection < 1:
					raise IndexError

				selected_download = filtered_files[int(num_selection) - 1][0]
				update_time = filtered_files[int(num_selection) - 1][1]
				print(f"Downloading {YELLOW}{selected_download}{RESET} (updated {YELLOW}{update_time}{RESET}) to {YELLOW}{destination_path}{RESET}")
			except (ValueError, IndexError):
				print(f" {RED}! Selected an invalid number{RESET}")
				selected_download = None
				continue

			## Query the GAR to download the selected file from the selected repository
			return_val = query_gar("download_file", selected_repo, selected_download)
			#print(return_val)

## Function
##  Returns the current menu location (the last item in the menu list)
def getCurrentMenuLocation():
	return menu[-1]

## Function
##  Adds the provided menu_item onto the queue (list) to properly keep track of where
##	 you are in the menu and what command you should call next.
def addToMenu(menu_item):
	global menu
	menu.append(menu_item)

## Function
##  Pops the most recent item off the menu queue (list) to properly keep track of where
##	 you are in the menu you are and what command you should call next.
def removeFromMenu():
	global selected_repo
	selected_repo = None

	global menu
	if len(menu) > 1:
		menu.pop()
	else:
		print(f" {RED}! Cannot remove the last item from the menu{RESET}")

## Function
##  Queries the GAR for the list of repositories or files based on the action provided.
def query_gar(action, repository, download_package):
	command = []
	error_message = None
	capture_output = True
	global destination_path

	## Setup the query based on the action
	if action == "list_repos":
		command = [gcloud_bin, "artifacts", "repositories", "list", "--project", project, "--location", location,
			 "--format=table(name, format)"]
		error_message = f" {RED}! Error listing repositories:{RESET} "
		#capture_output = True
	elif action == "list_files":
		command = [gcloud_bin, "artifacts", "files", "list", "--project", project, "--repository", repository,
			 "--location", location]
		error_message = f" {RED}! Error listing files:{RESET} "
		#capture_output = True
	elif action == "download_file":
		## Split the package type, version, and filename from the file object selected previously
		package, version, filename = download_package.split(":")
		## Build command to download the selected file from the selected repository
		command = [gcloud_bin, "artifacts", "generic", "download", "--project", project, "--repository", repository,
			"--location", location, "--package", package, "--version", version, "--name", filename, "--destination", destination_path]
		error_message = f" {RED}! Error downloading to {destination_path}{filename}:{RESET} "
		capture_output = False

	## Run the command based on the action and capture the output
	try:
		if capture_output:
			result = subprocess.run(command, capture_output=True, check=True, text=True)
		else:
			result = subprocess.run(command, capture_output=False, check=True, text=True)
	except subprocess.CalledProcessError as e:
		print(error_message, {e})
		return []

	return result

## Function
##  Filters the results from the query_gar function based on the action provided.
def filter_results(input_list, action):
	error_message = None

	# Store the repository names and formats in a list
	result = []
	if input_list:
		for line in input_list.stdout.strip().split("\n")[1:]:
			if line:
				if(action == "list_repos"):
					repo_name, repo_format = line.split()

					## Filter out repositories with the format "DOCKER"
					if repo_format == "DOCKER":
						continue
					else:
						## Save the repository name and format to the list of repositories
						result.append((repo_name, repo_format))
				elif(action == "list_files"):
					fields = line.split()

					## Filter the lines that are appened to the list of files
					if fields[0].startswith("sha256:"):
						continue
					else:
						## Save only the file name and update time to the list of files
						result.append((fields[0], fields[2]))
	else:
		print(f" {RED}! No repositories found.{RESET}")
		return []

	return result

## Function
##  Prints the list of repositories or files based on the action provided.
def print_list(data, action):
	# Check if the data is a list
	if not isinstance(data, list):
		print(f" {RED}! Data is not a list.{RESET}")
		return

	# Check if the list is empty
	if not data:
		print(f" {RED}! List is empty.{RESET}")
		return

	# Check if the list contains lists
	if (isinstance(item, list) for item in data):
		# Print the repository names and formats
		INDEX_WIDTH = 5
		COLUMN1_WIDTH = 40
		COLUMN2_WIDTH = 25

		if action == "list_repos":
			print(f"{'#':<{INDEX_WIDTH}}{'Repo':<{COLUMN1_WIDTH}}{'Format':<{COLUMN2_WIDTH}}")
			print(f"{'--':<{INDEX_WIDTH}}{'-----':<{COLUMN1_WIDTH}}{'------':<{COLUMN2_WIDTH}}")
		elif action == "list_files":
			COLUMN1_WIDTH = 110
			print(f"{'#':<{INDEX_WIDTH}}{'File':<{COLUMN1_WIDTH}}{'Updated':<{COLUMN2_WIDTH}}")
			print(f"{'--':<{INDEX_WIDTH}}{'-----':<{COLUMN1_WIDTH}}{'--------':<{COLUMN2_WIDTH}}")

		for index, (column1, column2) in enumerate(data, start=1):
			print(f"{index:<{INDEX_WIDTH}}"  # Aligns bracket space
				f"{column1:<{COLUMN1_WIDTH}}"
				f"{column2:<{COLUMN2_WIDTH}}")
		##print(data[1][0], data[1][1])  # Print the second repository's name and format
		return
	else:
		print(f" {RED}! List items are not lists{RESET}")
		## Print the plain list
		return

# This part sits at the very end and starts the program
if __name__ == "__main__":
    main()