from py_clob_client.client import ClobClient

from pmls.models import CancelOrderResponse

def cancel_all_orders(cli: ClobClient) -> CancelOrderResponse:
    resp = cli.cancel_all()
    return CancelOrderResponse(canceled=resp.get('canceled'), not_canceled=resp.get('not_canceled'))

def cancel_by_order_ids(cli: ClobClient, order_ids: list[str]) -> CancelOrderResponse:
    assert order_ids
    resp = cli.cancel_orders(order_ids)
    return CancelOrderResponse(canceled=resp.get('canceled'), not_canceled=resp.get('not_canceled'))

