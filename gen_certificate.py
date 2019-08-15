from TrainingGov import TrainingGovAPI, TrainingComponents
import json
from pprint import pprint
import requests
from datetime import datetime
import multiprocessing

api = TrainingGovAPI("WebService.Read", "Asdf098")
orgs = TrainingComponents()
search = orgs.search(unit=True)
results = search.Results.TrainingComponentSummary


def get_cert_rel(cert_details, type):
    src_cert_code = cert_details.Code
    dst_cert_code = cert_details.MappingInformation.Mapping[0].MapsToCode

    if type == '0':
        src_cert_code, dst_cert_code = dst_cert_code, src_cert_code

    data = {
        'src_cert_code': src_cert_code,
        'dst_cert_code': dst_cert_code,
        'rel_type': type,
        'isequivalent': cert_details.MappingInformation.Mapping[0].IsEquivalent,
        'note': cert_details.MappingInformation.Mapping[0].Notes,
    }

    r = requests.post("http://10.0.1.22:7010/reg:supersed-certificate-type/certificate-type--relation",
                      json=data)
    print('cert_rel', cert_details.Code, r.status_code, r.json())


def get_cert(code):
    cert_details = orgs.getDetails(code)['response']
    usage = cert_details.UsageRecommendations.UsageRecommendation
    releases = cert_details.Releases.Release

    for release in releases:
        if release['ReleaseNumber'] == str(len(releases)):
            status = release.Currency

    cert_data = {
        'title': cert_details.Title,
        'code': cert_details.Code,
        'description': "",
        'training_package_code': cert_details.ParentCode,
        'status': status,
        'version': len(cert_details.Releases.Release),
        'usage_recommendation': usage[len(usage) - 1].State,
        'release_date': str(usage[0].StartDate),
        'registrar_id': None,
    }
    print(cert_data)
    r = requests.post("http://10.0.1.22:7010/reg:create-certificate-type/certificate-type",
                      json=cert_data)
    print('cert', cert_details.Code, r.status_code, r.json())
    if r.status_code != 200:
        print('===============')
    if cert_details.MappingInformation is not None:
        for mapping in cert_details.MappingInformation.Mapping:
            get_cert(mapping.MapsToCode)


def gen_cert_rel(code):
    cert_details = orgs.getDetails(code)['response']

    if cert_details.MappingInformation is not None:
        for mapping in cert_details.MappingInformation.Mapping:
            get_cert_rel(cert_details, '1')
            get_cert_rel(cert_details, '0')
            gen_cert_rel(mapping.Code)


if __name__ == '__main__':
    for result in results:
        get_cert(result.Code)
    for result in results:
        get_cert_rel(result.Code)
