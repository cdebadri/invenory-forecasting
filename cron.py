from crontab import CronTab
import argparse
from getpass import getuser

if __name__ == '__main__':
	cron = CronTab(user=getuser())
	parser = argparse.ArgumentParser()
	parser.add_argument('--minutes', type=int) 
	args = parser.parse_args()


	if args.minutes != None:
		print('calling %d' % args.minutes)
		job = cron.new(command='python3 inventory_forecasting.py production')
		scheduling_string = str(args.minutes) + ' * * * *'
		job.setall(scheduling_string)
	else:
		job = cron.new(command='python3 inventory_forecasting.py production')
		job.setall('0 0 * * 0')

	cron.write()