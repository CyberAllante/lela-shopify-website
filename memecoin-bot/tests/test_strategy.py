"""Unit tests for the entry/exit decision logic."""

import time

from bot.config import StrategyConfig
from bot.engine.strategy import SniperStrategy
from bot.models import ExitReason, Position, TokenEvent


def make_strategy(**overrides):
    cfg = StrategyConfig(
        buy_amount_sol=0.05,
        take_profit_pct=0.5,
        stop_loss_pct=0.3,
        trailing_stop_pct=0.25,
        max_hold_seconds=600,
        max_open_positions=3,
    )
    for k, v in overrides.items():
        setattr(cfg, k, v)
    return SniperStrategy(cfg)


def make_position(entry=1.0, **overrides):
    pos = Position(
        mint="m" * 44,
        symbol="TEST",
        entry_price_sol=entry,
        token_amount=100.0,
        cost_sol=0.05,
    )
    for k, v in overrides.items():
        setattr(pos, k, v)
    return pos


def new_event(price=1e-7):
    return TokenEvent(mint="x" * 44, symbol="NEW", name="New", price_sol=price)


# ----- entry tests -------------------------------------------------------


def test_enters_fresh_token_with_room_and_cash():
    s = make_strategy()
    assert s.should_enter(new_event(), open_count=0, balance_sol=1.0, already_held=False)


def test_does_not_enter_when_already_held():
    s = make_strategy()
    assert not s.should_enter(new_event(), 0, 1.0, already_held=True)


def test_does_not_enter_when_at_position_cap():
    s = make_strategy(max_open_positions=3)
    assert not s.should_enter(new_event(), open_count=3, balance_sol=1.0, already_held=False)


def test_does_not_enter_without_enough_cash():
    s = make_strategy(buy_amount_sol=0.5)
    assert not s.should_enter(new_event(), 0, balance_sol=0.1, already_held=False)


def test_does_not_enter_without_a_price():
    s = make_strategy()
    assert not s.should_enter(new_event(price=None), 0, 1.0, already_held=False)


def test_respects_entry_price_band():
    s = make_strategy(min_entry_price_sol=1e-6)
    assert not s.should_enter(new_event(price=1e-8), 0, 1.0, already_held=False)


# ----- exit tests --------------------------------------------------------


def test_take_profit_triggers():
    s = make_strategy(take_profit_pct=0.5)
    pos = make_position(entry=1.0)
    assert s.check_exit(pos, current_price_sol=1.6) == ExitReason.TAKE_PROFIT


def test_stop_loss_triggers():
    s = make_strategy(stop_loss_pct=0.3)
    pos = make_position(entry=1.0)
    assert s.check_exit(pos, current_price_sol=0.65) == ExitReason.STOP_LOSS


def test_no_exit_in_neutral_zone():
    s = make_strategy()
    pos = make_position(entry=1.0)
    assert s.check_exit(pos, current_price_sol=1.1) is None


def test_trailing_stop_triggers_after_peak():
    s = make_strategy(take_profit_pct=5.0, trailing_stop_pct=0.25)
    pos = make_position(entry=1.0)
    # Climb to 2.0 (sets the peak), no exit yet since TP is far away.
    assert s.check_exit(pos, current_price_sol=2.0) is None
    assert pos.peak_price_sol == 2.0
    # Fall 25% from the peak (2.0 -> 1.5) should trail-stop us out.
    assert s.check_exit(pos, current_price_sol=1.5) == ExitReason.TRAILING_STOP


def test_trailing_stop_disabled_when_zero():
    s = make_strategy(take_profit_pct=5.0, trailing_stop_pct=0.0, stop_loss_pct=0.9)
    pos = make_position(entry=1.0)
    s.check_exit(pos, current_price_sol=2.0)
    # Big drop from peak but trailing disabled and still above stop-loss.
    assert s.check_exit(pos, current_price_sol=1.2) is None


def test_max_hold_triggers():
    s = make_strategy(max_hold_seconds=100)
    pos = make_position(entry=1.0, opened_at=time.time() - 200)
    assert s.check_exit(pos, current_price_sol=1.05) == ExitReason.MAX_HOLD


def test_take_profit_takes_priority_over_max_hold():
    s = make_strategy(take_profit_pct=0.5, max_hold_seconds=1)
    pos = make_position(entry=1.0, opened_at=time.time() - 100)
    assert s.check_exit(pos, current_price_sol=2.0) == ExitReason.TAKE_PROFIT
