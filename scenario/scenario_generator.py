import os

def generate_routes():

	if not os.path.exists('trips'):
		os.makedirs('trips')

	command = ("python /usr/share/sumo/tools/randomTrips.py --validate "
				"-n /home/eros/Documentos/Projects/securesimulation/scenario/{0}.net.xml "
				"-o trips/{0}_{1}.trips.xml "
				"-s {2}")

	for city in ['austin', 'chicago']:
		for i in range(33):
			os.system(command.format(city, i, i))


def generate_cfg():

	if not os.path.exists('cfgs'):
		os.makedirs('cfgs')

	for city in ['austin', 'chicago']:
		for i in range(33):
			file = open('cfgs/{0}_{1}.sumo.cfg'.format(city, i), 'w')
			file.write(("<configuration>\n"
					    "\t<input>\n"
					    "\t\t<net-file value='../{0}.net.xml'/>\n"
					    "\t\t<route-files value='../trips/{0}_{1}.trips.xml'/>\n"
					    "\t</input>\n"
						"</configuration>").format(city, i))

generate_cfg()