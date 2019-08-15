from datetime import date
import logging
from io import StringIO, BytesIO

from suds.client import Client
import suds
from suds.wsse import *
from suds.transport.https import WindowsHttpAuthenticated
from pprint import pprint


class TrainingGovAPI:
    security = Security()

    def __init__(self, username, password):
        self.username = username
        self.password = password

        self.token = UsernameToken(self.username, self.password)
        self.security.tokens.append(self.token)


class TrainingComponents(TrainingGovAPI):
    baseurl = "https://ws.sandbox.training.gov.au/Deewr.Tga.WebServices/TrainingComponentServiceV2.svc?wsdl"
    client = Client(baseurl)
    # print(client)

    def __init__(self):
        self.client.set_options(wsse=TrainingGovAPI.security)

    def search(self, filterTerm=None, searchCode=True, searchTitle=False,
               trainingpackage=False, qualification=False, skillset=False,
               unit=False):
        request = self.client.factory.create('TrainingComponentSearchRequest')

        # search term
        request.Filter = filterTerm

        # searches by unit/qual/course code
        request.SearchCode = searchCode

        # searches by uniit/qual/course title
        request.SearchTitle = searchTitle

        # Filtering options for the types of components returned by a search
        request.TrainingComponentTypes = [{
            "IncludeAccreditedCourse": 0,
            "IncludeAccreditedCourseModule": 0,
            "IncludeQualification": qualification,
            "IncludeSkillSet": skillset,
            "IncludeTrainingPackage": trainingpackage,
            "IncludeUnit": unit,
            "IncludeUnitContextualisation": 0
        }]

        return self.client.service.Search(request)

    def getClass(self):
        return self.client.service.GetClassificationSchemes()

    def getDetails(self, code, showDeprecated=True):
        request = self.client.factory.create('TrainingComponentDetailsRequest')

        request.Code = code
        try:
            result = self.client.service.GetDetails(request)
            if result.ComponentType == "Qualification":

                parsed_result = {
                    "type": result.ComponentType,
                    "response": result,
                    "title": result.Title,
                    "currency_status": result.CurrencyStatus,
                    "release_count": len(result.Releases["Release"]),
                    "releases": self.__buildReleases(result.Releases),
                    "training_package": {
                        "code": result.ParentCode,
                        "title": result.ParentTitle
                    }
                }

            elif result.ComponentType == "Unit":

                parsed_result = {
                    "type": result.ComponentType,
                    "response": result,
                    "title": result.Title,
                    "currency_status": result.CurrencyStatus
                }

            elif result.ComponentType == "TrainingPackage":

                parsed_result = {
                    # "type": result.ComponentType,
                    "response": result,
                    # "title": result.Title,
                    # "currency_status": result.CurrencyStatus
                }

            return parsed_result

        except suds.WebFault as e:

            return e

    def __buildReleases(self, releasesArr):
        # Iterating through the Qual and building unit dict
        releases = []
        for index, value in enumerate(releasesArr["Release"]):
            release = {
                "currency": value.Currency,
                "date": value.ReleaseDate,
                "number": value.ReleaseNumber,
            }

            # Check if release has a unit grid
            # Some releases don't for some reason
            if value.UnitGrid is not None:
                release["units"] = self.__buildUnitGrid(value.UnitGrid)
            else:
                # Return an empty array if no units
                release["units"] = []

            # Check if release has files
            if value.Files is not None:
                release["files"] = {
                    "pdf": {
                        "path": value.Files["ReleaseFile"][0].RelativePath,
                        "size": value.Files["ReleaseFile"][0].Size
                    },
                    "xml": {
                        "path": value.Files["ReleaseFile"][1].RelativePath,
                        "size": value.Files["ReleaseFile"][1].Size
                    },
                    "doc": {
                        "path": value.Files["ReleaseFile"][2].RelativePath,
                        "size": value.Files["ReleaseFile"][2].Size
                    }
                }
            else:
                release["files"] = []

            releases.append(release)
        return releases

    def __buildUnitGrid(self, unitGridArray):
        units = []
        for unit in unitGridArray["UnitGridEntry"]:
            unit = {
                "code": unit.Code,
                "title": unit.Title
            }
            units.append(unit)
        return units


class Organisations(TrainingGovAPI):
    baseurl = "https://ws.sandbox.training.gov.au/Deewr.Tga.WebServices/OrganisationServiceV2.svc?wsdl"
    client = Client(baseurl)

    def __init__(self):
        self.client.set_options(wsse=TrainingGovAPI.security)

    def getCourseList(self, rto_code, max_end_date=date.today()):
        """Returns a formatted dicts of qualifications and courses

        Keyword arguments:
        rto_code - training.gov.au registered RTO code
        max_end_date - date(yyyy,m,d) restricts end date of results
        """

        request = self.client.factory.create('OrganisationDetailsRequest')
        request.IncludeLegacyData = 0
        request.InformationRequested = [{
            "ShowCodes": 1,
            "ShowContacts": 0,
            "ShowExplicitScope": 1,
            "ShowDataManagers": 0,
            "ShowImplicitScope": 0,
            "ShowLocations": 0,
            "ShowRegistrationManagers": 0,
            "ShowRegistrationPeriods": 0,
            "ShowResponsibleLegalPersons": 0,
            "ShowRestrictions": 0,
            "ShowRtoClassifications": 1,
            "ShowRtoDeliveryNotification": 0,
            "ShowTradingNames": 0,
            "ShowUrls": 0
        }]

        request.Code = rto_code
        Organisations.result = self.client.service.GetDetails(request)

        scopes = Organisations.result["Scopes"][0]
        accredited_courses = []
        qualifications = []
        for item in scopes:
            component_type = item.TrainingComponentType
            if item.EndDate > max_end_date:
                if component_type == "Qualification":
                    qualifications.append(item)
                elif component_type == "AccreditedCourse":
                    accredited_courses.append(item)
        formatted_result = {
            "response": Organisations.result,
            "qualifications": qualifications,
            "accredited_courses": accredited_courses,
            "qualification_codes": self.__getCodes(qualifications),
            "accredited_course_codes": self.__getCodes(accredited_courses)
        }

        return formatted_result

    def __getCodes(self, components):
        codes = []
        for component in components:
            codes.append(component.NrtCode)
        return sorted(codes)
