import requests
import statistics
import matplotlib.pyplot as plt

def download_url(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(f"Error with downloading data: {e}")
        return None

def download_frankfurter(year):
    url = f"https://api.frankfurter.app/{year}-01-01..{year}-12-31?to=PLN"
    json = download_url(url)
    if not json: 
        print(f"There is no data for year {year}")
        return []

    months = [[] for _ in range(12)]
    for date, rates in json.get("rates", {}).items():
        if (year != int(date[0:4])): continue
        month = int(date[5:7])
        months[month-1].append(rates["PLN"])
    
    return [statistics.mean(m) if m else 0 for m in months]

def download_nbp(year):
    url = f"http://api.nbp.pl/api/exchangerates/rates/A/EUR/{year}-01-01/{year}-12-31/?format=json"    
    json = download_url(url)
    if not json: 
        print(f"There is no data for year {year}")
        return []

    months = [[] for _ in range(12)]
    for rate in json.get("rates", []):
        date = rate["effectiveDate"]
        if (year != int(date[0:4])): continue
        month = int(date[5:7])
        months[month-1].append(rate["mid"])
        
    return [statistics.mean(m) if m else 0 for m in months]

def predict(nbp_23, fran_23, nbp_24, fran_24):
    y23 = [(nbp_23[i] + fran_23[i])/2 for i in range(12)]
    y24 = [(nbp_24[i] + fran_24[i])/2 for i in range(12)]

    predicted_year = []
    base = y24[11]

    for i in range(12):        
        if i == 0:
            change = y24[0] - y23[11]
        else:
            change_23 = y23[i] - y23[i-1]
            change_24 = y24[i] - y24[i-1]
            change = (change_23 + change_24) / 2

        base += change
        predicted_year.append(base)

    return predicted_year

def display(F, title, oy_nbp, oy_fran, min_price, max_price):
    ox = range(1, 13)
    if oy_nbp:
        F.plot(ox, oy_nbp, label='NBP', marker='o', color='blue')
    if oy_fran:
        F.plot(ox, oy_fran, label='Frankfurter', marker='.', linestyle='--', color='red')
        
    F.set_title(title)
    F.set_ylabel("Price of 1 EUR in PLN")
    F.set_xlabel("Months")
    if oy_fran or oy_nbp:
        F.legend()
    F.grid(True)
    F.set_ylim(min_price, max_price)
    F.set_xticks(ox)
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    F.set_xticklabels(month_names)



fig, (F1, F2, F3) = plt.subplots(3, 1, figsize=(10, 14))
fig.suptitle('Euro exchange rate comparison', fontsize=14)

oy_nbp_23 = download_nbp(2023)
oy_fran_23 = download_frankfurter(2023)

oy_nbp_24 = download_nbp(2024)
oy_fran_24 = download_frankfurter(2024)

oy_predict_25 = predict(oy_nbp_23, oy_fran_23, oy_nbp_24, oy_fran_24)

all_data = oy_nbp_23 + oy_nbp_24 + oy_fran_23 + oy_fran_24 + oy_predict_25
if all_data:
    min_price = min(all_data) - 0.05
    max_price = max(all_data) + 0.05
else:
    min_price = 4
    max_price = 5

display(F1, "Year 2023", oy_nbp_23, oy_fran_23, min_price, max_price)
display(F2, "Year 2024", oy_nbp_24, oy_fran_24, min_price, max_price)

display(F3, "Prediction for year 2025", None, None, min_price, max_price)
F3.plot(range(1, 13), oy_predict_25, label='Prediction 2025', marker='D', color='maroon')
F3.legend()

plt.tight_layout(rect=[0, 0.03, 1, 0.95], h_pad=3.0)
plt.show()