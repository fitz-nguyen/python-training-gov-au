from TrainingGov import TrainingGovAPI, TrainingComponents
import json
from pprint import pprint
import requests
from datetime import datetime

api = TrainingGovAPI("WebService.Read", "Asdf098")
orgs = TrainingComponents()
orgs = TrainingComponents()
search = orgs.search()

results = search.Results.TrainingComponentSummary
for result in results:
    detail = orgs.getDetails(result.Code)

    data = {
        'title': result.Title,
        'code': result.Code,
        'usage_recommendation': detail['response'].UsageRecommendations.UsageRecommendation[0].State,
        # 'release_date': detail['response'].UsageRecommendations.UsageRecommendation[0].StartDate
        'release_date': "2011-6-7"
    }
    pprint(data)
    r = requests.post("http://localhost:8088/reg:create-training-package/training-package", json=data)
    print(r.status_code)
    break
