DATE_FORMATTER = "value != undefined ? new Date(value).toLocaleString('fr=FR', {dateStyle:'medium'}): ''"
CURRENCY_FORMATTER = "x.toLocaleString('fr-FR', {style: 'currency', currency: 'EUR'})"
YEAR_GETTER = "new Date(data.DATE).getFullYear()"
MONTH_GETTER = "new Date(data.DATE).toLocaleDateString('en-US',options={year:'numeric', month:'2-digit'})"

TITLE = "PEE Freitas 🏆"
SUBTITLE = "Cette application permet de visualiser les charges du PEE Freitas 📊"
