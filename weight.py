import statsapi
from tqdm import tqdm
import numpy as np
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
import pickle

### Load win rate data
data = {}

for year in tqdm(range(1969,2024)):
    table = statsapi.standings_data(season=year)
    for div in table.keys():
        for datum in table[div]["teams"]:
            name = datum['name']
            rate = datum['w'] / (datum['w'] + datum['l'])
            if name in data.keys():
                data[name].append(rate)
            else:
                data[name] = [rate]
                
with open('data.pkl', 'wb') as f:
    pickle.dump(data, f)


### Make rate pair
    
data = pickle.load(open('data.pkl', 'rb'))
rate_pair = []

def logit(p):
    return np.log(p/(1-p))
def inv_logit(p):
    return 1/(1+np.exp(-p))

for name in tqdm(data.keys()):
    for i in range(len(data[name])-1):
        rate_pair.append((logit(data[name][i]), logit(data[name][i+1])))
        rate_pair.append((logit(1-data[name][i]), logit(1-data[name][i+1])))
        
### Linear regression

X = np.array([x[0] for x in rate_pair]).reshape(-1,1)
y = np.array([x[1] for x in rate_pair])

reg = LinearRegression().fit(X, y)
mse = mean_squared_error(y, reg.predict(X))
Sxx = np.sum((X - np.mean(X))**2)

real_data_rate = [86/142, 79/141, 76/141, 75/142, 74/142, 73/142, 68/144, 61/143, 58/138, 58/141]
real_data = [[logit(x)] for x in real_data_rate]

predicted = list(reg.predict(real_data))
sd = [np.sqrt(mse * (1 + 1/len(X) + (x - np.mean(X))**2 / Sxx)) for x in real_data]
Z = [(real_data[i][0] - predicted[i]) / sd[i] for i in range(len(real_data))]
percentile = [1 - stats.norm.cdf(z) for z in Z]

better_weight = [(0.5/percentile[i])**2 for i in range(len(real_data))]
worse_weight = [(0.5/(1-percentile[i]))**2 for i in range(len(real_data))]

team_names = ["LG", "KT", "SSG", "NC", "두산", "KIA", "롯데", "삼성", "한화", "키움"]

print("Team\t2023\tBetter\tWorse")
for i in range(len(real_data)):
    print(f"{team_names[i]}\t{real_data_rate[i]:.3f}\t{float(better_weight[i]):.3f}\t{float(worse_weight[i]):.3f}")
    
weight = [[team_names[i] ,better_weight[i], worse_weight[i]] for i in range(len(real_data))]
with open('weight.pkl', 'wb') as f:
    pickle.dump(weight, f)






