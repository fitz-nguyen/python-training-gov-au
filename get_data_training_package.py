from TrainingGov import TrainingGovAPI, TrainingComponents
import json
from pprint import pprint
import requests
from datetime import datetime
api = TrainingGovAPI("WebService.Read", "Asdf098")
orgs = TrainingComponents()
search = orgs.search(trainingpackage=True)
results = search.Results.TrainingComponentSummary


def get_trainingpackage(code):
    detail = orgs.getDetails(code)['response']
    usage = detail.UsageRecommendations.UsageRecommendation
    train_data = {
        'title': detail.Title,
        'code': detail.Code,
        'usage_recommendation': usage[len(usage) - 1].State,
        'release_date': str(detail.UsageRecommendations.UsageRecommendation[0].StartDate)
    }
    r = requests.post("http://10.0.1.22:7010/reg:create-training-package/training-package",
                      json=train_data)
    print('training_package', detail.Code, r.status_code, r.json())

    if detail.MappingInformation is not None:
        print('supersed')
        for mapping in detail.MappingInformation.Mapping:
            get_trainingpackage(mapping.MapsToCode)

    # if detail.ReverseMappingInformation is not None:
    #     get_trainingpackage(detail.ReverseMappingInformation.Mapping[0].MapsToCode)


if __name__ == '__main__':
    for result in results:
        get_trainingpackage(result.Code)
