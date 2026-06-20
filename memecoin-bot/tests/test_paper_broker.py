"""Unit tests for the paper broker and portfolio accounting."""

import pytest

from bot.engine.paper_broker import InsufficientFunds, PaperBroker
from bot.engine.portfolio import Portfolio
from bot.models import ExitReason


def make_broker(balance=1.0, fee=0.0, slippage=0.0):
    return PaperBroker(starting_balance_sol=balance, fee_pct=fee, slippage_pct=slippage)


def test_buy_debits_balance_and_sizes_position():
    b = make_broker(balance=1.0, fee=0.0, slippage=0.0)
    pos = b.buy("mint", "TKN", quoted_price_sol=0.001, spend_sol=0.1)
    assert b.balance_sol == pytest.approx(0.9)
    assert pos.cost_sol == pytest.approx(0.1)
    assert pos.token_amount == pytest.approx(0.1 / 0.001)


def test_buy_applies_fee_and_slippage():
    b = make_broker(balance=1.0, fee=0.01, slippage=0.02)
    pos = b.buy("mint", "TKN", quoted_price_sol=0.001, spend_sol=0.1)
    # Fee reduces SOL that buys tokens; slippage raises the fill price.
    fill_price = 0.001 * 1.02
    sol_for_tokens = 0.1 * (1 - 0.01)
    assert pos.entry_price_sol == pytest.approx(fill_price)
    assert pos.token_amount == pytest.approx(sol_for_tokens / fill_price)


def test_buy_rejects_insufficient_funds():
    b = make_broker(balance=0.05)
    with pytest.raises(InsufficientFunds):
        b.buy("mint", "TKN", quoted_price_sol=0.001, spend_sol=0.1)


def test_round_trip_profit_with_no_costs():
    b = make_broker(balance=1.0, fee=0.0, slippage=0.0)
    pos = b.buy("mint", "TKN", quoted_price_sol=0.001, spend_sol=0.1)
    trade = b.sell(pos, quoted_price_sol=0.002, reason=ExitReason.TAKE_PROFIT)
    # Doubled price with no fees => ~2x proceeds.
    assert trade.proceeds_sol == pytest.approx(0.2)
    assert trade.pnl_sol == pytest.approx(0.1)
    assert trade.pnl_pct == pytest.approx(1.0)
    assert b.balance_sol == pytest.approx(1.1)


def test_costs_eat_into_a_flat_round_trip():
    b = make_broker(balance=1.0, fee=0.01, slippage=0.02)
    pos = b.buy("mint", "TKN", quoted_price_sol=0.001, spend_sol=0.1)
    # Sell at the same quoted price: fees + slippage should make it a small loss.
    trade = b.sell(pos, quoted_price_sol=0.001, reason=ExitReason.MANUAL)
    assert trade.pnl_sol < 0
    assert b.balance_sol < 1.0


def test_portfolio_tracks_and_reports():
    pf = Portfolio()
    b = make_broker(balance=1.0)
    pos = b.buy("mint", "TKN", quoted_price_sol=0.001, spend_sol=0.1)
    pf.add(pos)
    assert pf.open_count == 1
    assert pf.has("mint")

    pf.remove("mint")
    trade = b.sell(pos, quoted_price_sol=0.002, reason=ExitReason.TAKE_PROFIT)
    pf.record_close(trade)
    assert pf.open_count == 0
    assert pf.wins == 1
    assert pf.win_rate == 1.0
    assert pf.realized_pnl_sol > 0
