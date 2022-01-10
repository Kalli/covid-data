import pandas as pd
import seaborn as sns
from matplotlib.dates import MonthLocator, DateFormatter
from matplotlib.ticker import FixedLocator
import matplotlib.pyplot as plt

# thanks color hunt https://colorhunt.co/palette/2e4c6d396eb0daddfcfc997c
first = '#2E4C6D'
second = '#FC997C'
third = '#DADDFC'
fourth = '#396EB0'

sns.set_theme(style='white', font_scale=0.75, font='Helvetica')
background_colour = first
sns.set_theme(rc={
    'axes.facecolor': first, 'figure.facecolor': first, 
    'axes.edgecolor': second, 'patch.edgecolor': second,
    'axes.labelcolor': second, 'text.color': second, 
	'ytick.color': second, 'xtick.color': second, 
	'grid.color': second, 
	'figure.figsize': (10, 10),
})

def load_trust_in_gov():
	trust_in_gov = pd.read_csv('./data/OECD-trust-in-government.csv', comment="#")
	# get the most recent measurement 
	trust_in_gov = trust_in_gov.sort_values('TIME', ascending=False)
	trust_in_gov = trust_in_gov.drop_duplicates(['LOCATION'])
	trust_in_gov = trust_in_gov.set_index('LOCATION')
	return trust_in_gov

# trust = load_trust_in_gov()

def load_owid_covid(scatter_key, hue_key):
	owid_covid = pd.read_csv('./data/owid-covid-data.csv', comment="#")

	# the attribute we want to use for the scatterplot hue
	hue = owid_covid.dropna(subset=[hue_key,])
	hue = hue.sort_values('date', ascending=False)
	hue = hue.drop_duplicates(['iso_code']).set_index('iso_code')
	hue = hue.filter([hue_key])

	# get the most recent measurement for our key
	owid_covid = owid_covid.dropna(subset=[scatter_key,])
	owid_covid = owid_covid.sort_values('date', ascending=False)
	owid_covid = owid_covid.drop_duplicates(['iso_code']).set_index('iso_code')
	owid_covid = owid_covid.filter(['location', scatter_key])
	return owid_covid, hue

owid_key = 'people_fully_vaccinated_per_hundred'
hue = 'human_development_index'
# vaccinated, hdi= load_owid_covid(owid_key, hue)

def scatter(joined, hue_key):
	ax = sns.scatterplot(
		x='Value',
		y=owid_key,
		data=joined,
		legend=True,
		hue=hue_key,
		palette=sns.color_palette("rocket", as_cmap=True),
	)
	_, labels = ax.get_legend_handles_labels()
	ax.legend(
		title='Human Development Index:', 
		loc='lower left', 
	)

	ax.set(ylim=(0, joined[owid_key].max()*1.05), xlim=(0, 100))
	ax.set_yticklabels(['{:,.0f}'.format(x).replace(',', '.')  for x in ax.get_yticks()])
	ax.set_xticklabels(['{:,.0f}%'.format(x) for x in ax.get_xticks()])

	corr = 'Correlation {0:10.2f}'.format(joined['Value'].corr(joined[owid_key]))

	ax.set_title(label='Covid outcomes and Trust in Government', fontsize=16, weight='bold')
	ax.set_xlabel('Trust in government (most recent available measurement)')
	ax.set_ylabel(owid_key.replace('_', ' ').title() + ' (Jan 2022)')

	ax = set_footer(
		ax, [
			'* Our World in Data: https://covid.ourworldindata.org/data/owid-covid-data.csv',
			'* OECD: https://data.oecd.org/gga/trust-in-government.htm',
		]
	)
	# add labels
	for line in range(0, joined.shape[0]):
		x, y, = 0.5, 0.5

		ax.text(
			joined.Value[line]+x, 
			joined[owid_key][line]+y, 
			joined.location[line], 
			horizontalalignment='left', 
			size='small',
			color=third,
		)

	ax.get_figure().savefig('./img/{0}_trust_in_government.svg'.format(owid_key))


def set_footer(ax, sources):
	footer_right = "\n".join(['Sources:'] + sources)
	ax.figure.text(x=0.55, y=0.01, s=footer_right, fontsize=8, alpha=0.75, color=second)
	
	footer_left = "\n".join([
		'Made by Karl Tryggvason',
		'@KarlTryggvason / KarlTryggvason.com',
		'https//github.com/kalli/covid-data',
	])
	ax.figure.text(x=0.005, y=0.01, s=footer_left, fontsize=8, alpha=0.75, color=second)
	return ax

# scatter(trust.join(vaccinated).join(hdi), hue)


def owid_data_by_country(country_iso, data_keys, data):
	df = data.dropna(subset=data_keys)
	df = df.sort_values('date', ascending=True)
	df = df[df['iso_code'] == country_iso]
	df = df.dropna(axis='columns')
	return df


def movement_data_by_country(country, area_id):
	# https://data.humdata.org/dataset/movement-range-maps
	# the full file is huge, so check to see if we have a cache
	file_path = './data/{0}-movement-range-data.txt'.format(country)
	try: 
		df = pd.read_csv(file_path, comment="#", parse_dates=['ds'])
	except: 
		df = pd.read_csv('./data/movement-range-data.txt', comment="#", sep='\t')
		df = df.sort_values('ds', ascending=True)
		df = df[(df['country'] == country) & (df['polygon_id'] == area_id)]
		df.to_csv(file_path, index=False)
	# 7 day rolling average
	key = 'all_day_bing_tiles_visited_relative_change'
	df['tiles_visited_7_day_rolling_average'] = df[key].rolling(window=7).mean() 
	return df


def movement_cases_lineplot(data, name, country, region):
	fig, ax = plt.subplots(3)

	g1 = sns.lineplot(
		ax = ax[0],
		data=data['new_cases_smoothed'],
		color=third,
	)
	g1.set_ylim(0, data['new_cases_smoothed'].max()* 1.05)
	g1.set_xlim(data.index.min(), data.index.max())
	title = 'Covid cases in {0} (7 day rolling average)'.format(country)
	g1.set_title(label=title, fontsize=16, weight='bold')
	g1.set_ylabel('New confirmed cases \n of COVID-19')
	g1.set_xlabel('')
	g1.grid(False)
	g1.set_xticklabels([])
	g1.yaxis.set_major_locator(FixedLocator(g1.get_yticks()))
	g1.set_yticklabels(['{:,.0f}'.format(x).replace(',', '.')  for x in g1.get_yticks()])

	g2 = sns.lineplot(
		ax = ax[1],
		data=data['stringency_index'],
		color=third,
	)
	g2.set_ylim(0, data['stringency_index'].max()* 1.05)
	g2.set_xlim(data.index.min(), data.index.max())
	title = 'Government Response Stringency Index'.format(country)
	g2.set_title(label=title, fontsize=16, weight='bold')
	g2.set_ylabel('Government Response \n Stringency Index')
	g2.set_xlabel('')
	g2.grid(False)
	g2.set_xticklabels([])

	g3 = sns.lineplot(
		ax = ax[2],
		data=data['tiles_visited_7_day_rolling_average'],
		color=third,
	)
	g3.set_xlim(data.index.min(), data.index.max())
	title = 'Change in Movement - {1} / {0}'.format(country, region)
	g3.set_title(label=title, fontsize=16, weight='bold')
	g3.set_ylabel('Relative change in movement\n (compared to February 2020 baseline)')
	ticks = g3.get_yticks()
	g3.yaxis.set_major_locator(FixedLocator(ticks))
	g3.set_yticklabels(['{:,.0f}%'.format(x*100).replace(',', '.')  for x in ticks])
	g3.set_xlabel('Date')
	g3.grid(False)

	fig = set_footer(fig, [
		'* Our World in Data: https://covid.ourworldindata.org/data/owid-covid-data.csv',
		'* Humanitarian Data Exchange: https://data.humdata.org/dataset/movement-range-maps',
	])
	g3.xaxis.set_major_locator(MonthLocator(interval=2, bymonthday=1))
	g3.xaxis.set_major_formatter(DateFormatter('%b %y'))
	g3.xaxis.set_minor_locator(MonthLocator(interval=1, bymonthday=1))
	g3.tick_params(which="both", bottom=True)
	fig.savefig('./img/{0}.svg'.format(name))


owid_covid = pd.read_csv('./data/owid-covid-data.csv', comment="#", parse_dates=['date'])
regions = [
	['ISL', 'ISL.3_1', 'Iceland', 'Capital Region'],
	['DNK', 'DNK.1_1', 'Denmark', 'Capital Region'],
	['NOR', 'NOR.12_1', 'Norway', 'Oslo'],
	['GBR', 'GBR.1_1', 'Great Britain', 'England'],
]

for r in regions:
	country_code, region_code, country_name, region_name = r
	country_covid = owid_data_by_country(country_code, ['new_cases_smoothed',  'stringency_index'], owid_covid).dropna()
	country_movement = movement_data_by_country(country_code, region_code)
	joined = country_movement.set_index('ds').join(country_covid.set_index('date'))
	joined = joined[['tiles_visited_7_day_rolling_average', 'new_cases_smoothed', 'stringency_index']]
	file_name = 'new_cases_stringency_movement_change_{0}'.format(country_name.lower().replace(" ", "_"))
	movement_cases_lineplot(joined, file_name, country_name, region_name)