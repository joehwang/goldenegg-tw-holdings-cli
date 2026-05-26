"""
Golden Egg command line interface.
"""

import argparse
import asyncio
import contextlib
import os
import sys
from typing import Any

from service.holdings_service import HoldingsService


DEFAULT_BROKERS = "fubon,esun,sinopac,tssco"


def _configure_keyring() -> None:
    os.environ.setdefault(
        "PYTHON_KEYRING_BACKEND",
        "keyrings.cryptfile.cryptfile.CryptFileKeyring",
    )


def _print_json(data: Any) -> None:
    print(HoldingsService.to_json(data, ensure_ascii=False, indent=2))


async def _handle_holdings(args: argparse.Namespace) -> int:
    with contextlib.redirect_stdout(sys.stderr):
        service = HoldingsService(
            cache_ttl_seconds=args.cache_ttl,
            cache_maxsize=args.cache_maxsize,
        )
        result = await service.get_holdings(
            broker=args.broker,
            update_prices=not args.no_update_prices,
            force_refresh=args.force_refresh,
        )

    if args.raw:
        _print_json(result)
    else:
        formatted_result = service.format_holdings_data_json(result, "股票庫存查詢")
        _print_json(formatted_result)

    return 0 if result.get("success") else 1


def _handle_brokers(_args: argparse.Namespace) -> int:
    with contextlib.redirect_stdout(sys.stderr):
        service = HoldingsService()
    _print_json(service.get_supported_brokers())
    return 0


def _handle_cache(args: argparse.Namespace) -> int:
    with contextlib.redirect_stdout(sys.stderr):
        service = HoldingsService(
            cache_ttl_seconds=args.cache_ttl,
            cache_maxsize=args.cache_maxsize,
        )

        if args.cache_action == "info":
            result = service.get_cache_info()
        elif args.cache_action == "clear":
            result = service.clear_cache()
        else:
            raise ValueError(f"Unknown cache action: {args.cache_action}")

    _print_json(result)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="golden-egg",
        description="台股券商庫存查詢命令列工具",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    brokers_parser = subparsers.add_parser(
        "brokers",
        help="列出支援的券商",
    )
    brokers_parser.set_defaults(handler=_handle_brokers)

    holdings_parser = subparsers.add_parser(
        "holdings",
        help="查詢持股資料",
    )
    holdings_parser.add_argument(
        "-b",
        "--broker",
        default=DEFAULT_BROKERS,
        help=(
            "券商代碼，可用逗號分隔多個券商；支援 fubon, esun, sinopac, "
            "tssco, all。預設查詢全部券商。"
        ),
    )
    holdings_parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="略過快取並重新呼叫券商 API",
    )
    holdings_parser.add_argument(
        "--no-update-prices",
        action="store_true",
        help="不更新即時價格",
    )
    holdings_parser.add_argument(
        "--raw",
        action="store_true",
        help="輸出未格式化的原始查詢結果",
    )
    holdings_parser.add_argument(
        "--cache-ttl",
        type=int,
        default=300,
        help="快取秒數，預設 300",
    )
    holdings_parser.add_argument(
        "--cache-maxsize",
        type=int,
        default=50,
        help="快取最大項目數，預設 50",
    )
    holdings_parser.set_defaults(handler=_handle_holdings)

    cache_parser = subparsers.add_parser(
        "cache",
        help="查看或清除本次命令執行期間的快取",
    )
    cache_parser.add_argument(
        "cache_action",
        choices=("info", "clear"),
        help="快取操作",
    )
    cache_parser.add_argument(
        "--cache-ttl",
        type=int,
        default=300,
        help="快取秒數，預設 300",
    )
    cache_parser.add_argument(
        "--cache-maxsize",
        type=int,
        default=50,
        help="快取最大項目數，預設 50",
    )
    cache_parser.set_defaults(handler=_handle_cache)

    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_keyring()
    parser = build_parser()
    args = parser.parse_args(argv)

    result = args.handler(args)
    if asyncio.iscoroutine(result):
        return asyncio.run(result)
    return result
