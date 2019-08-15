import asyncio
import time
import aiohttp
# import requests
# from TrainingGov import TrainingGovAPI, TrainingComponents
import uuid
import random


# async def download_site(session, url):
#     async with session.get(url) as response:
#         print("Read {0} from {1}".format(response.content_length, url))


# async def download_all_sites(sites):
#     async with aiohttp.ClientSession() as session:
#         tasks = []
#         for url in sites:
#             task = asyncio.ensure_future(download_site(session, url))
#             tasks.append(task)
#         await asyncio.gather(*tasks, return_exceptions=True)


async def download_site(session, result):
    # detail = orgs.getDetails(result.Code)
    # print(detail['response'].ComponentType, result.Code)

    # data = {
    #     'title': result.Title,
    #     'code': result.Code,
    #     'usage_recommendation': detail['response'].UsageRecommendations.UsageRecommendation[0].State,
    #     'release_date': str(detail['response'].UsageRecommendations.UsageRecommendation[0].StartDate)
    # }
    data = {
        'title': 'result.Title',
        'code': str(random.randrange(1000000000)),
        'usage_recommendation': 'detail.UsageRecommendations.UsageRecommendation[0].State',
        'release_date': '2011-03-01'
    }

    async with session.post('http://10.0.1.22:7010/reg:create-training-package/training-package', json=data) as response:
        print("Read {0} from {1}".format(response.content_length, str(uuid.uuid4())))
        print(response.status)


async def download_all_sites(results):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for result in range(results):
            task = asyncio.ensure_future(download_site(session, result))
            tasks.append(task)
        await asyncio.gather(*tasks, return_exceptions=True)


# if __name__ == "__main__":
#     sites = [
#         "https://www.jython.org",
#         "http://olympus.realpython.org/dice",
#     ] * 80
#     start_time = time.time()
#     asyncio.get_event_loop().run_until_complete(download_all_sites(sites))
#     duration = time.time() - start_time
#     print(f"Downloaded {len(sites)} sites in {duration} seconds")

if __name__ == "__main__":
    # api = TrainingGovAPI("WebService.Read", "Asdf098")
    # orgs = TrainingComponents()
    # search = orgs.search(trainingpackage=True)
    # results = search.Results.TrainingComponentSummary

    start_time = time.time()
    asyncio.get_event_loop().run_until_complete(download_all_sites(1000))
    duration = time.time() - start_time
    print(f"Downloaded {len(1000)} sites in {duration} seconds")
