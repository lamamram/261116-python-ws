from gorest_client.gorest import GoRestClient
from gorest_client.exceptions import ApiError
from requests.exceptions import ConnectionError, Timeout

if __name__ == "__main__":
    # api = GoRestClient()
    try:
        with GoRestClient() as api:
            # print(api.base_url)
            # print(list(api.list("users")))
            print(api.get("users", "018d0faa-b240-7d95-8cc2-479f04f365d7"))
    except (ConnectionError, Timeout) as e:
        print(e, type(e).__name__)
    except ApiError as e:
        print(e, type(e).__name__, e.problem)