from decimal import Decimal
from typing import AsyncGenerator, Optional

from jkit._base import DATA_OBJECT_CONFIG, DataObject, ResourceObject
from jkit._constraints import (
    NonEmptyStr,
    NormalizedDatetime,
    PositiveInt,
)
from jkit._network_request import get_json
from jkit._normalization import (
    normalize_assets_amount,
    normalize_assets_amount_precise,
    normalize_datetime,
)
from jkit.config import ENDPOINT_CONFIG
from jkit.credential import JianshuCredential


class AssetsTransactionRecord(DataObject, **DATA_OBJECT_CONFIG):
    id: PositiveInt  # noqa: A003
    time: NormalizedDatetime
    type_id: PositiveInt
    type_text: NonEmptyStr
    amount: float
    amount_precise: Decimal


class AssetsTransactionHistory(ResourceObject):
    def __init__(self, *, credential: JianshuCredential) -> None:
        self._credential = credential

    async def iter_fp_records(
        self, *, max_id: Optional[int] = None
    ) -> AsyncGenerator[AssetsTransactionRecord, None]:
        now_max_id = max_id

        while True:
            data = await get_json(
                endpoint=ENDPOINT_CONFIG.jianshu,
                path="/asimov/fp_wallets/transactions",
                params={"since_id": 0, "max_id": now_max_id}
                if now_max_id
                else {"since_id": 0},
                cookies=self._credential.cookies,
            )
            if not data["transactions"]:
                return

            now_max_id = data["transactions"][-1]["id"]

            for item in data["transactions"]:
                is_out = item["io_type"] == 2
                yield AssetsTransactionRecord(
                    id=item["id"],
                    time=normalize_datetime(item["time"]),
                    type_id=item["tn_type"],
                    type_text=item["display_name"],
                    amount=normalize_assets_amount(item["amount"])
                    * (-1 if is_out else 1),
                    amount_precise=normalize_assets_amount_precise(
                        item["amount_18"] * (-1 if is_out else 1)
                    ),
                )._validate()

    async def iter_ftn_records(
        self, *, max_id: Optional[int] = None
    ) -> AsyncGenerator[AssetsTransactionRecord, None]:
        now_max_id = max_id

        while True:
            data = await get_json(
                endpoint=ENDPOINT_CONFIG.jianshu,
                path="/asimov/fp_wallets/jsb_transactions",
                params={"since_id": 0, "max_id": now_max_id}
                if now_max_id
                else {"since_id": 0},
                cookies=self._credential.cookies,
            )
            if not data["transactions"]:
                return

            now_max_id = data["transactions"][-1]["id"]

            for item in data["transactions"]:
                is_out = item["io_type"] == 2
                yield AssetsTransactionRecord(
                    id=item["id"],
                    time=normalize_datetime(item["time"]),
                    type_id=item["tn_type"],
                    type_text=item["display_name"],
                    amount=normalize_assets_amount(item["amount"])
                    * (-1 if is_out else 1),
                    amount_precise=normalize_assets_amount_precise(
                        item["amount_18"] * (-1 if is_out else 1)
                    ),
                )._validate()
