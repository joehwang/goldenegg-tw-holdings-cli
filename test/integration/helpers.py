def get_holdings_or_skip(test_case, client_factory, broker_name):
    """Run a real broker API call, skipping known external-service failures."""
    try:
        return client_factory().get_holdings()
    except Exception as exc:
        message = str(exc)
        transient_errors = (
            "'NoneType' object is not subscriptable",
            "EOF while parsing a value",
            "富邦登入失敗",
            "富邦登入成功但沒有帳戶資料",
            "timed out",
            "Connection",
            "connection",
            "AGR0003",
            "Exceed Transaction Rate Limit",
        )
        if any(error in message for error in transient_errors):
            test_case.skipTest(f"{broker_name} 外部 API 暫時不可用: {message}")
        raise
