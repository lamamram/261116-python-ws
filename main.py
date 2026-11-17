from gorest_client.gorest import GoRestClient
from gorest_client.exceptions import ApiError
from requests.exceptions import ConnectionError, Timeout

if __name__ == "__main__":
    # api = GoRestClient()
    try:
        with GoRestClient() as api:
            # print(api.base_url)
            # print(list(api.list("users")))
            # print(api.get("users", "018d0faa-b240-7d95-8cc2-479f04f365d7"))
            # obj = api.post("users", {"name":"matt6 LAMAM6","email":"mlamamra6@example.com"})
            # obj, etag = api.get("users", obj["id"])
            # print(api.patch("users", obj["id"], {"status": "inactive"}, etag=etag))
            obj, etag = api.get("users", "01a1ea29-ade0-7563-b1e5-df991e6b5982")
            print(obj, etag, type(etag).__name__)
            print(api.patch(
                "users", 
                "01a1ea29-ade0-7563-b1e5-df991e6b5982", 
                {"status": "active"}, 
                etag=etag
            ))

    except (ConnectionError, Timeout) as e:
        print(e, type(e).__name__)
    except ApiError as e:
        print(e, type(e).__name__, e.problem)