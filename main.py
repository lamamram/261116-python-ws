from gorest_client.gorest import GoRestClient


if __name__ == "__main__":
    # api = GoRestClient()
    with GoRestClient() as api:
        # print(api.base_url)
        # print(list(api.list("users")))
        print(api.get("users", "019d00aa-b240-7d95-8cc2-479f04f365d7"))