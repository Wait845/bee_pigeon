from plugins import weather, api, exchange


task_list = [
    {
        "schedule": "*/1 * * * *",
        "uid": [
            {
                "bark": {"uuid": "aaaaaaaaaaaaaaa"}
            }
        ],
        "function": exchange.get_exchange_rate,
        "args": ("英镑",),
        "kwargs": {}
    },
    {
        "schedule": "*/1 * * * *",
        "function": api.notify_bark,
        "args": (
            ["aaaaaaaaaaaaa","bbbbbbbbbbbbbbb"],
            "hello, test"
        ),
        "kwargs": {}
    }
]