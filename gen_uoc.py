from TrainingGov import TrainingGovAPI, TrainingComponents
import json
from pprint import pprint
import requests
from datetime import datetime

api = TrainingGovAPI("WebService.Read", "Asdf098")
orgs = TrainingComponents()
search = orgs.search(unit=True)
results = search.Results.TrainingComponentSummary


def get_uoc_rel(uoc_details, type):
    src_uoc_code = uoc_details.Code
    dst_uoc_code = uoc_details.MappingInformation.Mapping[0].MapsToCode

    if type == '0':
        src_uoc_code, dst_uoc_code = dst_uoc_code, src_uoc_code

    data = {
        'src_uoc_code': src_uoc_code,
        'dst_uoc_code': dst_uoc_code,
        'rel_type': type,
        'isequivalent': uoc_details.MappingInformation.Mapping[0].IsEquivalent,
        'note': uoc_details.MappingInformation.Mapping[0].Notes,
    }

    r = requests.post("http://10.0.1.22:7010/reg:supersed-uoc/uoc-relation",
                      json=data)
    print('uoc_rel', uoc_details.Code, r.status_code, r.json())


def get_uoc(code):
    uoc_details = orgs.getDetails(code)['response']
    usage = uoc_details.UsageRecommendations.UsageRecommendation
    releases = uoc_details.Releases.Release

    for release in releases:
        if release['ReleaseNumber'] == str(len(releases)):
            status = release.Currency

    uoc_data = {
        'title': uoc_details.Title,
        'code': uoc_details.Code,
        'description': "",
        'training_package_code': uoc_details.ParentCode,
        'classification_code': uoc_details.Classifications.Classification[0].ValueCode,
        'status': status,
        'version': len(uoc_details.Releases.Release),
        'usage_recommendation': usage[len(usage) - 1].State,
        'release_date': str(usage[0].StartDate)
    }

    r = requests.post("http://10.0.1.22:7010/reg:create-uoc/uoc",
                      json=uoc_data)
    print('uoc', uoc_details.Code, r.status_code, r.json())
    if r.status_code != 200:
        print('===============')
    if uoc_details.MappingInformation is not None:
        for mapping in uoc_details.MappingInformation.Mapping:
            get_uoc(mapping.MapsToCode)


def gen_uoc_rel(code):
    uoc_details = orgs.getDetails(code)['response']

    if uoc_details.MappingInformation is not None:
        for mapping in uoc_details.MappingInformation.Mapping:
            get_uoc_rel(uoc_details, '1')
            get_uoc_rel(uoc_details, '0')
            gen_uoc_rel(mapping.Code)


if __name__ == '__main__':
    for result in results:
        get_uoc(result.Code)
    for result in results:
        get_uoc_rel(result.Code)
