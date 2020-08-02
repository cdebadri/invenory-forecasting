# invenory-forecasting
Ensure you're running Python 3.x

Other data source: https://www.kaggle.com/c/demand-forecasting-kernels-only/data

To run the script with other data use:
python inventory_forecasting.py trial --path <full/path/to/train.csv>

To run the script with data on db:
python inventory_forecasting.py production

To run it as a cron job after every 'n' minutes
python cron.py --minutes <value of n>

To run it as a cron weekly:
python cron.py
