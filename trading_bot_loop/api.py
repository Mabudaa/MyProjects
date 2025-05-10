from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
import MetaTrader5 as MetaTrader5

app = Flask(__name__)
mt5.initialize()

app.config['SQLALCHEMY_DATABASE_URL'] = 'sqlite:///trading.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
	db.create_all()


class Symbol(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name=db.Column(db.String(10), unique=True, nullable=False)
	digits = db.Column(db.Float, nullable=False)
	contract_size = db.Column(db.Integer, nullable=False)
	enabled = db.Column(db.Boolean, default=True)

	def to_dict(self):
		return{'name':self.name, "digits":self.digits, 'contract_size':self.contract_size}


class Equity(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	equity = db.Column(db.Float, unique=True, nullable=False)
	timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnnow)

class NewsEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(10), db.ForeignKey('symbol.name'), nullable=False)
    event_name = db.Column(db.String(255), nullable=False)
    event_time = db.Column(db.DateTime, nullable=False)
	
#####################################################################@ POSITIONS @###############################################################################

def split_and_add_to_list(statement, existing_list=None):
	words = statement.split(',')
	if existing_list is None:
		existing_list = []
	existing_list.extend(words)
	
	return existing_list

@app.route('/open_trades', methods = ['GET'])
def get_open_trades():
	positions = mt5.positions_get()
	if positions:
		grouped_trades = {}

		for position in positions:
			trade_id = position.ticket
			symbol = position.symbol
			comment = position.comment
			timeframe = split_and_add_to_list(position.comment)[1]

			if timeframe not in grouped_trades:
				grouped_trades[timeframe] = []

			grouped_trades[timeframe].append({
				"id": trade_id,
				"symbol":symbol,
				"timeframe":timeframe,
				"volume":position.volume,
				"price_open":position.price_open,
				})
	else:
		return jsonify({'error':"Failed to retrieve positions"})
	return jsonify(grouped_trades), 200

import MetaTrader5 as mt5

@app.route('/positions', methods=['GET'])
def get_positions():
    mt5.initialize()
    positions = mt5.positions_get()
    if positions is None:
        return jsonify({'status': 'error', 'message': 'No open positions'})
    
    formatted_positions = []
    for pos in positions:
        timeframe = split_and_add_to_list(position.comment)[1]  # Extract timeframe from comment
        formatted_positions.append({
            'id': pos.ticket,
            'symbol': pos.symbol,
            'volume': pos.volume,
            'price_open': pos.price_open,
            'timeframe': timeframe
        })

    return jsonify({'status': 'success', 'positions': formatted_positions})

@app.route('/positions/<symbol>', methods=['GET'])
def get_symbol_positions(symbol):
    mt5.initialize()
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return jsonify({'status': 'error', 'message': f'No open positions for {symbol}'})

    formatted_positions = []
    for pos in positions:
        formatted_positions.append({
            'id': pos.ticket,
            'symbol': pos.symbol,
            'volume': pos.volume,
            'price_open': pos.price_open
        })

    return jsonify({'status': 'success', 'positions': formatted_positions})

@app.route('/positions/<symbol>/grouped', methods=['GET'])
def get_positions_grouped(symbol):
    mt5.initialize()
    positions = mt5.positions_get(symbol=symbol)
    if positions is None:
        return jsonify({'status': 'error', 'message': f'No open positions for {symbol}'})

    grouped_positions = {}
    for pos in positions:
        comment_parts = pos.comment.split(',')
        timeframe = comment_parts[0]  # Extract timeframe from comment
        if timeframe not in grouped_positions:
            grouped_positions[timeframe] = []
        grouped_positions[timeframe].append({
            'id': pos.ticket,
            'symbol': pos.symbol,
            'volume': pos.volume,
            'price_open': pos.price_open
        })

    return jsonify({'status': 'success', 'grouped_positions': grouped_positions})


############################################################################@ SYMBOLS @##############################################################################

@app.route('/symbols', methods=['POST'])
def add_symbol():
    data = request.json
    new_symbol = Symbol(
        name=data['name'], 
        digits=data['digits'], 
        contract_size=data['contract_size']
    )
    db.session.add(new_symbol)
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Symbol {data["name"]} added'})

@app.route('/symbols', methods=['GET'])
def get_symbols():
    symbols = Symbol.query.all()
    return jsonify({'symbols': [{'name': s.name, 'enabled': s.enabled} for s in symbols]})

@app.route('/symbols/<symbol>', methods=['PATCH'])
def toggle_symbol(symbol):
    s = Symbol.query.filter_by(name=symbol).first()
    if not s:
        return jsonify({'status': 'error', 'message': 'Symbol not found'}), 404
    s.enabled = not s.enabled
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Symbol {symbol} {"enabled" if s.enabled else "disabled"}'})

@app.route('/symbols/<symbol>', methods=['DELETE'])
def remove_symbol(symbol):
    s = Symbol.query.filter_by(name=symbol).first()
    if not s:
        return jsonify({'status': 'error', 'message': 'Symbol not found'}), 404
    db.session.delete(s)
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'Symbol {symbol} removed'})


######################################################################@ EQUITY CURVE @############################################################################

@app.route('/equity_curve', methods = ['GET'])

def get_equity_curve():
	equity_data = Equity.query.all()
	equity_list = [{'timestamp': eq.timestamp, 'equity': eq.equity} for eq in equity_data]

	return jsonify(equity_list)		

	db.session.commit()
	return jsonify({'message': f'{name} enabled for trading'})


@app.route('/symbols', methods = ['GET'])
def get_symbols():
	symbols = Symbol.query.all()
	return jsonify([symbol.to_dict() for symbol in symbols])



############################################################ @News Events@ ####################################################

@app.route('/symbols/<symbol>/news', methods=['GET'])
def get_news_events(symbol):
    news_events = NewsEvent.query.filter_by(symbol=symbol).all()
    return jsonify({
        'status': 'success',
        'news_events': [{'id': e.id, 'event_name': e.event_name, 'event_time': e.event_time.strftime('%Y-%m-%d %H:%M:%S')}
                        for e in news_events]
    })

@app.route('/symbols/<symbol>/news/<int:event_id>', methods=['DELETE'])
def delete_news_event(symbol, event_id):
    news_event = NewsEvent.query.filter_by(symbol=symbol, id=event_id).first()
    if not news_event:
        return jsonify({'status': 'error', 'message': 'News event not found'}), 404

    db.session.delete(news_event)
    db.session.commit()
    return jsonify({'status': 'success', 'message': f'News event {event_id} removed for {symbol}'})


@app.route('/symbols/<symbol>/news', methods=['POST'])
def add_news_event(symbol):
    data = request.json
    event_time = datetime.strptime(data['event_time'], '%Y-%m-%d %H:%M:%S')

    # Check if symbol exists
    symbol_exists = Symbol.query.filter_by(name=symbol).first()
    if not symbol_exists:
        return jsonify({'status': 'error', 'message': 'Symbol not found'}), 404

    news_event = NewsEvent(symbol=symbol, event_name=data['event_name'], event_time=event_time)
    db.session.add(news_event)
    db.session.commit()
    
    return jsonify({'status': 'success', 'message': f'News event "{data["event_name"]}" added for {symbol}'})

if __name__ == '__main__':
	app.run(debug = True, host = )
