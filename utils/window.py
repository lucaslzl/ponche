import numpy as np
import matplotlib.pyplot as plt


def clean_window(window_scores):

	new_window = [float('{0:.2f}'.format(x)) for x in window_scores]
	print(new_window)


def identify_spots(window_scores):

	print([indx for indx, x in enumerate(window_scores) if x != 0.0])
	

def plot_to_see():


	window_scores = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.5, 1.0, 0.5, 0.05, 
					0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 0.41, 0.5, 0.09, 
					0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.01, 0.18, 0.58, 
					0.27, 0.02, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
					0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
					0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.12, 0.53, 0.37, 
					0.04, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
					0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.05, 
					0.41, 0.5, 0.09, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
					0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 
					0.01, 0.15, 0.56, 0.32, 0.03]

	startsticks = [6, 20, 34, 75, 106, 137]
	endsticks = [14, 27, 42, 82, 113, 144]

	plt.clf()
	plt.figure(1)
	plt.subplot(211)

	plt.plot(range(0, 144), window_scores, '--', color='#656565', linewidth=2.5)

	plt.xticks(np.arange(0, 145, 6), ['' for x in np.arange(0, 25)])
	plt.grid(False)
	plt.xlabel('Hours of the day', fontweight='bold')
	plt.ylabel('Score', fontweight='bold')

	plt.plot(startsticks, [0.04 for x in startsticks], 'v', color='#07654B')
	plt.plot(endsticks, [0.04 for x in endsticks], 'v', color='#960A15')

	#plt.show()
	plt.savefig('windows.pdf', bbox_inches="tight", format='pdf')


plot_to_see()
