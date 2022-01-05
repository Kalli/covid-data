import pandas as pd
import seaborn as sns

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
	"figure.figsize": (10, 10),
})

trust_in_gov = pd.read_csv('./data/OECD-trust-in-government.csv', comment="#")

# get the most recent measurement 
trust_in_gov = trust_in_gov.sort_values('TIME', ascending=False)
trust_in_gov = trust_in_gov.drop_duplicates(['LOCATION'])

owid_covid = pd.read_csv('./data/owid-covid-data.csv', comment="#")

# the attribute we want to use for a hue
hue_key = 'human_development_index'
hue = owid_covid.dropna(subset=[hue_key,])
hue = hue.sort_values('date', ascending=False)
hue = hue.drop_duplicates(['iso_code']).set_index('iso_code')
hue = hue.filter([hue_key])

# select a key to use
owid_key = 'people_fully_vaccinated_per_hundred'
# get the most recent measurement for our key
owid_covid = owid_covid.dropna(subset=[owid_key,])
owid_covid = owid_covid.sort_values('date', ascending=False)
owid_covid = owid_covid.drop_duplicates(['iso_code']).set_index('iso_code')
owid_covid = owid_covid.filter(['location', owid_key])

# join the frames
trust_in_gov = trust_in_gov.set_index('LOCATION')
joined = trust_in_gov.join(owid_covid).join(hue)

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

footer_right = "\n".join([
	'Sources:',
	'* Our World in Data: https://covid.ourworldindata.org/data/owid-covid-data.csv',
	'* OECD: https://data.oecd.org/gga/trust-in-government.htm',
])
ax.figure.text(x=0.6, y=0.01, s=footer_right, fontsize=8, alpha=0.75)

footer_left = "\n".join([
	'Made by Karl Tryggvason',
	'@KarlTryggvason / KarlTryggvason.com',
	'https//github.com/kalli/covid-data',
])
ax.figure.text(x=0.005, y=0.01, s=footer_left, fontsize=8, alpha=0.75)


# laborious manual label placement... 
offsets = {}
if owid_key == 'total_deaths_per_million': 
	_x = 1
	_y = 1
	CENTER = -20
	LOWER = -50
	offsets = {
		'France': [1, CENTER],
		'Greece': [1, LOWER],
		'Lithuania': [1, LOWER],
		'Norway': [1, CENTER],
		'Poland': [1, LOWER],
		'Slovenia': [1, 15],
		'South Korea': [1, LOWER],
		'Switzerland': [1, CENTER],
	}

if owid_key == 'people_fully_vaccinated_per_hundred': 
	_x = 0.5
	_y = 0.5
	CENTER = -0.3
	LOWER = -1
	offsets = {
		'Brazil': [0.5, CENTER],
		'Costa Rica': [-10, CENTER],
		'Czechia': [0.5, LOWER],
		'Estonia': [0.5, CENTER],
		'Finland': [0.5, CENTER],
		'Germany': [0.5, CENTER],
		'Israel': [0.5, CENTER],
		'Iceland': [1, 0.5],
		'Ireland': [0.5, LOWER],
		'Norway': [0.5, CENTER],
		'Slovenia': [0.5, CENTER],
		'South Korea': [0.5, CENTER],
		'Sweden': [0.5, CENTER],
		'Switzerland': [0.5, CENTER],
		'Turkey': [0.5, CENTER],
		'United Kingdom': [0.5, CENTER],
		'United States': [0.5, LOWER],
	}


# add labels
for line in range(0, joined.shape[0]):
	x, y, = offsets.get(joined.location[line], [_x, _y])

	ax.text(
		joined.Value[line]+x, 
		joined[owid_key][line]+y, 
     	joined.location[line], 
		horizontalalignment='left', 
     	size='small',
		color=third,
	)

ax.get_figure().savefig('./img/{0}_trust_in_government.svg'.format(owid_key))