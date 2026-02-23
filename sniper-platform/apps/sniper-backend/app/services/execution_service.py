from __future__ import annotations

from datetime import datetime
from pathlib import Path
from uuid import uuid4

import joblib
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.brokers.base import BaseBroker
from app.brokers.dhan import DhanBroker
from app.brokers.paper_trading import PaperTradingBroker
from app.brokers.upstox import UpstoxBroker
from app.brokers.zerodha import ZerodhaBroker
from app.config import Settings
from app.core.execution_engine.cost_estimator import CostEstimator
from app.core.execution_engine.order_router import SmartOrderRouter
from app.core.execution_engine.order_router_quantum import QuantumOrderRouter, QuantumRoutingConfig
from app.core.execution_engine.rl_agent import PPOExecutionAgent
from app.core.risk_engine.greeks_calculator import GreeksCalculator
from app.models.database.audit import AuditLog
from app.models.database.execution import BrokerAccount, Order, OrderEvent, PnlDaily, PnlIntraday, PositionSnapshot, Trade
from app.utils.convex_bus import ConvexBus
from app.utils.encryption import DataEncryptor
from app.utils.logger import get_logger
from app.utils.market_data import get_market_data_service

logger = get_logger(__name__)


class ExecutionService:
    def __init__(
        self,
        settings: Settings,
        quantum_service,
        risk_service,
        event_bus: ConvexBus | None = None,
        session_factory: async_sessionmaker | None = None,
        encryptor: DataEncryptor | None = None,
    ) -> None:
        self.settings = settings
        self.quantum_service = quantum_service
        self.risk_service = risk_service
        self.event_bus = event_bus
        self.session_factory = session_factory
        self.encryptor = encryptor
        self.cost_estimator = CostEstimator()
        self.rl_agent = PPOExecutionAgent()
        self.greeks_calculator = GreeksCalculator()
        self.classical_router = SmartOrderRouter()
        self.quantum_router = QuantumOrderRouter()
        self.broker = self._build_broker()
        self._active_broker_account_id: str | None = None
        self.orders: dict[str, dict] = {}
        self.trades: dict[str, dict] = {}

    def _build_broker(self) -> BaseBroker:
        provider = (self.settings.broker_provider or 'paper').strip().lower()

        if provider == 'zerodha':
            broker = ZerodhaBroker()
            broker.connect({'api_key': self.settings.zerodha_api_key, 'api_secret': self.settings.zerodha_api_secret})
            if broker.connected:
                return broker
            logger.warning('Zerodha selected but credentials missing/invalid. Falling back to paper broker.')
            provider = 'paper'

        if provider == 'upstox':
            broker = UpstoxBroker()
            broker.connect(
                {
                    'api_key': self.settings.upstox_api_key,
                    'api_secret': self.settings.upstox_api_secret,
                    'redirect_uri': self.settings.upstox_redirect_uri,
                    'access_token': self.settings.upstox_access_token,
                }
            )
            if broker.connected:
                return broker
            logger.warning('Upstox selected but credentials missing/invalid. Falling back to paper broker.')
            provider = 'paper'

        if provider == 'dhan':
            broker = DhanBroker()
            broker.connect({'api_key': self.settings.zerodha_api_key, 'api_secret': self.settings.zerodha_api_secret})
            if broker.connected:
                return broker
            logger.warning('Dhan selected but credentials missing/invalid. Falling back to paper broker.')

        if provider not in {'paper', 'zerodha', 'upstox', 'dhan'}:
            logger.warning("Unknown broker_provider '%s'. Falling back to paper broker.", provider)

        broker = PaperTradingBroker()
        broker.connect({})
        return broker

    def load_models(self, models_dir: str) -> None:
        path = Path(models_dir) / 'ppo_execution.joblib'
        if path.exists():
            artifact = joblib.load(path)
            if 'weights' in artifact:
                self.rl_agent.weights = artifact['weights']

    async def ensure_broker_account(self) -> None:
        provider = (self.settings.broker_provider or 'paper').strip().lower()
        if provider == 'paper' or self.session_factory is None:
            self._active_broker_account_id = None
            return

        credentials = {k: v for k, v in self._build_broker_credentials(provider).items() if v not in (None, '')}
        if not credentials or 'account_id' not in credentials:
            logger.warning('Broker provider is %s but no credentials were provided.', provider)
            return

        if self.encryptor is None:
            raise ValueError('DATA_ENCRYPTION_KEY is required when using a live broker provider')

        encrypted_credentials = self.encryptor.encrypt_json(credentials)
        account_id = str(credentials.get('account_id') or 'primary')

        async with self.session_factory() as session:
            existing = (
                await session.execute(
                    select(BrokerAccount).where(
                        BrokerAccount.user_id == self.settings.default_user_uuid,
                        BrokerAccount.provider == provider,
                        BrokerAccount.account_id == account_id,
                    )
                )
            ).scalars().first()

            if existing is None:
                existing = BrokerAccount(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    provider=provider,
                    account_id=account_id,
                    encrypted_credentials=encrypted_credentials,
                    token_expires_at=None,
                    is_active=True,
                )
                session.add(existing)
                action = 'broker_account_create'
            else:
                existing.encrypted_credentials = encrypted_credentials
                existing.is_active = True
                action = 'broker_account_rotate'

            session.add(
                AuditLog(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    entity_type='broker_account',
                    entity_id=existing.id,
                    action=action,
                    details={'provider': provider, 'account_id': account_id},
                    source='startup',
                )
            )
            await session.commit()
            self._active_broker_account_id = existing.id

    def _build_broker_credentials(self, provider: str) -> dict:
        if provider == 'upstox':
            return {
                'api_key': self.settings.upstox_api_key,
                'api_secret': self.settings.upstox_api_secret,
                'redirect_uri': self.settings.upstox_redirect_uri,
                'access_token': self.settings.upstox_access_token,
                'account_id': 'primary',
            }
        if provider == 'zerodha':
            return {
                'api_key': self.settings.zerodha_api_key,
                'api_secret': self.settings.zerodha_api_secret,
                'account_id': 'primary',
            }
        if provider == 'dhan':
            return {
                'api_key': self.settings.zerodha_api_key,
                'api_secret': self.settings.zerodha_api_secret,
                'account_id': 'primary',
            }
        return {}

    async def place_order(self, payload: dict) -> dict:
        symbol = payload['symbol']
        quantity = int(payload['quantity'])
        raw_side = payload['side']
        side = raw_side.value if hasattr(raw_side, 'value') else str(raw_side)

        if not self.risk_service.check_pre_trade({'delta': quantity if side == 'BUY' else -quantity, 'gamma': 0.0}):
            raise ValueError('pre-trade risk check failed')

        # Fetch live price; fall back to payload price or 100.0 if unavailable
        live_price = await get_market_data_service().aget_price(symbol)
        resolved_price = live_price or float(payload.get('price') or 100.0)
        market_state = {
            'price': resolved_price,
            'spread': 0.05,
            'avg_daily_volume': 2_000_000,
            'instrument_type': str(payload.get('instrument_type', 'EQ')).upper(),
        }

        if self.settings.enable_quantum_routing and quantity * market_state['price'] >= self.settings.quantum_routing_min_order_size:
            decision = self.quantum_router.route({'quantity': quantity}, market_state, QuantumRoutingConfig())
            self.quantum_service.record_solve('routing', decision.solve_time_ms, decision.expected_cost, True)
        else:
            decision = self.classical_router.route({'quantity': quantity}, market_state)

        costs = self.cost_estimator.estimate_total_cost(
            symbol=symbol,
            quantity=quantity,
            order_type=decision.order_type,
            urgency=float(payload.get('urgency', 0.5)),
            market_state=market_state,
            side=side,
        )

        broker_order = self.broker.place_order(
            symbol=symbol,
            quantity=quantity,
            order_type=decision.order_type,
            price=market_state['price'],
            side=side,
        )

        order_status = str(broker_order.get('status', 'PENDING')).upper()
        filled_qty = int(broker_order.get('filled_qty', quantity if order_status == 'COMPLETE' else 0))
        avg_price = broker_order.get('avg_price')
        if avg_price is None and filled_qty > 0:
            avg_price = market_state['price']

        order_id = str(uuid4())
        order = {
            'id': order_id,
            'symbol': symbol,
            'side': side,
            'quantity': quantity,
            'order_type': decision.order_type,
            'status': order_status,
            'price': market_state['price'],
            'filled_qty': filled_qty,
            'avg_price': avg_price,
            'strategy_id': payload.get('strategy_id'),
            'broker_account_id': self._active_broker_account_id,
            'timestamp': datetime.utcnow(),
            'costs': costs.__dict__,
            'routing': decision.__dict__,
        }
        self.orders[order_id] = order

        if self.session_factory is not None:
            async with self.session_factory() as session:
                session.add(
                    Order(
                        id=order_id,
                        user_id=self.settings.default_user_uuid,
                        strategy_id=payload.get('strategy_id'),
                        broker_account_id=self._active_broker_account_id,
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        order_type=decision.order_type,
                        price=market_state['price'],
                        status=order_status,
                        filled_qty=filled_qty,
                        avg_price=avg_price,
                        routing_data=self._json_ready(decision.__dict__),
                        cost_data=self._json_ready(costs.__dict__),
                        timestamp=order['timestamp'],
                    )
                )
                session.add(
                    OrderEvent(
                        id=str(uuid4()),
                        order_id=order_id,
                        event_type='placed',
                        status=order_status,
                        message='order accepted by broker',
                        payload=self._json_ready(order),
                    )
                )

                if filled_qty > 0 and avg_price is not None:
                    session.add(
                        Trade(
                            id=str(uuid4()),
                            user_id=self.settings.default_user_uuid,
                            order_id=order_id,
                            symbol=symbol,
                            side=side,
                            quantity=filled_qty,
                            entry_price=float(avg_price),
                            exit_price=None,
                            pnl=0.0,
                            fees=float(costs.total),
                            entry_time=datetime.utcnow(),
                            exit_time=None,
                        )
                    )

                positions = await self.get_positions()
                for pos in positions:
                    session.add(
                        PositionSnapshot(
                            id=str(uuid4()),
                            user_id=self.settings.default_user_uuid,
                            symbol=str(pos['symbol']),
                            quantity=int(pos['quantity']),
                            avg_price=float(pos['avg_price']),
                            current_price=float(pos['current_price']),
                            pnl=float(pos['pnl']),
                            delta=float(pos.get('delta', 0.0)),
                            gamma=float(pos.get('gamma', 0.0)),
                            theta=float(pos.get('theta', 0.0)),
                            vega=float(pos.get('vega', 0.0)),
                            as_of=datetime.utcnow(),
                            is_eod=False,
                        )
                    )

                symbol_upper = str(symbol).upper()
                target_position = next(
                    (pos for pos in positions if str(pos.get('symbol', '')).upper() == symbol_upper), None
                )
                if target_position is not None:
                    unrealized = float(target_position.get('pnl', 0.0))
                    session.add(
                        PnlIntraday(
                            id=str(uuid4()),
                            user_id=self.settings.default_user_uuid,
                            symbol=symbol_upper,
                            realized_pnl=0.0,
                            unrealized_pnl=unrealized,
                            net_pnl=unrealized,
                            as_of=datetime.utcnow(),
                        )
                    )

                trade_date = datetime.utcnow().date()
                existing_daily = (
                    await session.execute(
                        select(PnlDaily).where(
                            PnlDaily.user_id == self.settings.default_user_uuid,
                            PnlDaily.trade_date == trade_date,
                        )
                    )
                ).scalars().first()
                portfolio_unrealized = float(sum(float(pos.get('pnl', 0.0)) for pos in positions))
                if existing_daily is None:
                    session.add(
                        PnlDaily(
                            id=str(uuid4()),
                            user_id=self.settings.default_user_uuid,
                            trade_date=trade_date,
                            realized_pnl=0.0,
                            unrealized_pnl=portfolio_unrealized,
                            gross_pnl=portfolio_unrealized,
                            net_pnl=portfolio_unrealized,
                        )
                    )
                else:
                    existing_daily.unrealized_pnl = portfolio_unrealized
                    existing_daily.gross_pnl = portfolio_unrealized
                    existing_daily.net_pnl = portfolio_unrealized

                session.add(
                    AuditLog(
                        id=str(uuid4()),
                        user_id=self.settings.default_user_uuid,
                        entity_type='order',
                        entity_id=order_id,
                        action='place',
                        details={'symbol': symbol, 'side': side, 'quantity': quantity},
                        source='api',
                    )
                )
                await session.commit()

        self._emit_order_update(order)
        self._emit_position_update(symbol)

        if filled_qty > 0 and avg_price is not None:
            trade_id = str(uuid4())
            self.trades[trade_id] = {
                'id': trade_id,
                'order_id': order_id,
                'symbol': symbol,
                'side': side,
                'quantity': filled_qty,
                'entry_price': avg_price,
                'exit_price': None,
                'pnl': 0.0,
                'entry_time': datetime.utcnow(),
                'exit_time': None,
            }
        return order

    async def list_orders(self, status: str | None = None, strategy_id: str | None = None) -> list[dict]:
        if self.session_factory is None:
            orders = list(self.orders.values())
            if status:
                orders = [o for o in orders if o['status'] == status]
            if strategy_id:
                orders = [o for o in orders if o.get('strategy_id') == strategy_id]
            return orders

        async with self.session_factory() as session:
            query = select(Order).order_by(Order.timestamp.desc())
            if status:
                query = query.where(Order.status == status)
            if strategy_id:
                query = query.where(Order.strategy_id == strategy_id)
            rows = (await session.execute(query)).scalars().all()
            return [self._order_row_to_dict(row) for row in rows]

    async def get_order(self, order_id: str) -> dict:
        if self.session_factory is None:
            return self.orders[order_id]
        async with self.session_factory() as session:
            row = await session.get(Order, order_id)
            if row is None:
                raise KeyError(order_id)
            return self._order_row_to_dict(row)

    async def cancel_order(self, order_id: str) -> dict:
        if self.session_factory is None:
            order = self.orders[order_id]
            order['status'] = 'CANCELLED'
            self._emit_order_update(order)
            return order

        async with self.session_factory() as session:
            row = await session.get(Order, order_id)
            if row is None:
                raise KeyError(order_id)
            row.status = 'CANCELLED'
            session.add(
                OrderEvent(
                    id=str(uuid4()),
                    order_id=order_id,
                    event_type='cancelled',
                    status='CANCELLED',
                    message='cancelled by user',
                    payload={},
                )
            )
            session.add(
                AuditLog(
                    id=str(uuid4()),
                    user_id=self.settings.default_user_uuid,
                    entity_type='order',
                    entity_id=order_id,
                    action='cancel',
                    details={'status': 'CANCELLED'},
                    source='api',
                )
            )
            await session.commit()
            await session.refresh(row)
            order = self._order_row_to_dict(row)
            self._emit_order_update(order)
            return order

    async def get_positions(self) -> list[dict]:
        positions = self.broker.get_positions()
        mds = get_market_data_service()
        for pos in positions:
            symbol = str(pos.get('symbol', ''))
            qty = int(pos.get('quantity', 0))

            # Refresh current price with live market data
            live_price = await mds.aget_price(symbol)
            if live_price is not None:
                pos['current_price'] = live_price
                avg = float(pos.get('avg_price', live_price))
                pos['pnl'] = (live_price - avg) * qty
            pos.setdefault('current_price', float(pos.get('avg_price', 0.0)))

            # Calculate Greeks
            instrument_type = str(pos.get('instrument_type', 'EQ')).upper()
            if instrument_type == 'OPTION' and pos.get('strike') and pos.get('expiry'):
                try:
                    g = self.greeks_calculator.calculate_single_option(
                        spot=float(pos.get('current_price', 100.0)),
                        strike=float(pos['strike']),
                        expiry=float(pos['expiry']),
                        volatility=float(pos.get('volatility', 0.2)),
                        option_type=str(pos.get('option_type', 'CALL')),
                        risk_free_rate=float(pos.get('risk_free_rate', 0.06)),
                    )
                    pos['delta'] = round(g.delta * qty, 4)
                    pos['gamma'] = round(g.gamma * qty, 6)
                    pos['theta'] = round(g.theta * qty, 4)
                    pos['vega'] = round(g.vega * qty, 4)
                except Exception:
                    pos.setdefault('delta', 0.0)
                    pos.setdefault('gamma', 0.0)
                    pos.setdefault('theta', 0.0)
                    pos.setdefault('vega', 0.0)
            else:
                # Equity/futures: delta = net quantity, other Greeks = 0
                pos['delta'] = float(qty)
                pos.setdefault('gamma', 0.0)
                pos.setdefault('theta', 0.0)
                pos.setdefault('vega', 0.0)
        return positions

    async def list_trades(self, strategy_id: str | None = None, symbol: str | None = None) -> list[dict]:
        if self.session_factory is None:
            trades = list(self.trades.values())
            if strategy_id:
                order_ids = {o['id'] for o in self.orders.values() if o.get('strategy_id') == strategy_id}
                trades = [t for t in trades if t['order_id'] in order_ids]
            if symbol:
                trades = [t for t in trades if t['symbol'] == symbol]
            return trades

        async with self.session_factory() as session:
            query = select(Trade).order_by(Trade.entry_time.desc())
            if symbol:
                query = query.where(Trade.symbol == symbol)
            rows = (await session.execute(query)).scalars().all()
            data = [
                {
                    'id': row.id,
                    'order_id': row.order_id,
                    'symbol': row.symbol,
                    'side': row.side,
                    'quantity': row.quantity,
                    'entry_price': row.entry_price,
                    'exit_price': row.exit_price,
                    'pnl': row.pnl,
                    'entry_time': row.entry_time,
                    'exit_time': row.exit_time,
                }
                for row in rows
            ]
            if strategy_id:
                allowed_orders = {
                    item['id']
                    for item in await self.list_orders(status=None, strategy_id=strategy_id)
                }
                data = [row for row in data if row['order_id'] in allowed_orders]
            return data

    def _emit_order_update(self, order: dict) -> None:
        if self.event_bus is None:
            return
        normalized = self._json_ready(order)
        channel_symbol = str(order.get('symbol') or '').upper()
        self.event_bus.publish_event_nowait('order:update', 'order:update', {'order': normalized})
        if channel_symbol:
            self.event_bus.publish_event_nowait(
                f'order:update:{channel_symbol}',
                'order:update',
                {'order': normalized},
            )
        self.event_bus.set_json_nowait(f"order:last:{order['id']}", normalized, ttl_seconds=86400)

    def _emit_position_update(self, symbol: str | None = None) -> None:
        if self.event_bus is None:
            return
        positions = [self._json_ready(pos) for pos in self.broker.get_positions()]
        payload = {'positions': positions}
        channel = 'position:update'
        if symbol:
            channel = f'position:update:{str(symbol).upper()}'
            payload['symbol'] = str(symbol).upper()
        self.event_bus.publish_event_nowait(channel, 'position:update', payload)
        self.event_bus.publish_event_nowait('position:update', 'position:update', payload)

        if symbol:
            target = next((pos for pos in positions if str(pos.get('symbol')).upper() == str(symbol).upper()), None)
            if target:
                self.event_bus.set_json_nowait(f'position:latest:{str(symbol).upper()}', target, ttl_seconds=86400)

    def _json_ready(self, value):
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, dict):
            return {key: self._json_ready(val) for key, val in value.items()}
        if isinstance(value, list):
            return [self._json_ready(item) for item in value]
        return value

    def _order_row_to_dict(self, row: Order) -> dict:
        return {
            'id': row.id,
            'strategy_id': row.strategy_id,
            'broker_account_id': row.broker_account_id,
            'symbol': row.symbol,
            'side': row.side,
            'quantity': row.quantity,
            'order_type': row.order_type,
            'price': row.price,
            'status': row.status,
            'filled_qty': row.filled_qty,
            'avg_price': row.avg_price,
            'timestamp': row.timestamp,
            'routing': row.routing_data or {},
            'costs': row.cost_data or {},
        }
