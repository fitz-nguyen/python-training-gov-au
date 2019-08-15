from TrainingGov import TrainingGovAPI, TrainingGovAPI, TrainingComponents
from suds.sudsobject import asdict
import requests

api = TrainingGovAPI("WebService.Read", "Asdf098")
quals = TrainingComponents()
results = quals.getClass().NrtClassificationSchemeResult
sum = 0
for result in results:
    paths = result.ClassificationValues.ClassificationValue
    sum += len(paths)
    for path in paths:
        value = str(path.Value)
        title = path.Name
        scheme = result.Description
        class_data = {
            'scheme': scheme,
            'title': title,
            'code': value,
            'release_date': '2011-03-01'
        }
        r = requests.post("http://localhost:7010/reg:create-classification/classification",
                          json=class_data)
        print(r.status_code, r.content)
        # if r.status_code != 200:
        #     print('error')
        #     break
