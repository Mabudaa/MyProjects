# Trading Bot Controller Apps

This project is a mobile-based trading bot controller built with **React Native (Expo)** for the frontend and **Flask** for the backend API. It communicates with a trading bot running in **MetaTrader 5** through a custom Flask API. The app allows traders to manage symbols, monitor trades, visualize equity changes, and control trading activity with ease.

---

## Features
- View, add, and delete symbols for trading
- View open trades grouped by timeframe
- Visualize equity history
- Add and manage news events that may impact trading
- Input and persist the IP address of the trading bot
- Toggle trading activity per symbol

---

## Disclaimer
This project includes a simulated strategy for demonstration purposes. The real trading strategy is not included for proprietary and risk management reasons. Trading in financial markets involves risk, and past performance does not guarantee future results.

---

## Flask API
The backend Flask API is responsible for:
- Connecting to MetaTrader5
- Managing the trading logic and strategy (running in a separate thread)
- Handling API routes for symbol management, trade grouping, equity tracking, and news events

### Strategy Threading
The trading bot strategy runs in a background thread to ensure the API remains responsive. This structure allows the app to interact with the bot in real-time without blocking.

---

## Dependencies
### Flask API (Python)
- Flask
- MetaTrader5
- SQLAlchemy
- APScheduler

### React Native App (Expo)
- React Navigation
- AsyncStorage
- TailwindCSS for styling (via className to style converter)

---

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/trading-bot-controller.git
cd trading-bot-controller
```

### 2. Set Up the Flask API (Backend)
> Requires Python 3.8+, MetaTrader5 installed, and terminal access.

```bash
cd flask-api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
python app.py
```

Make sure MetaTrader5 is installed and configured correctly. The Flask API will start the trading bot in a separate thread.

### 3. Set Up the React Native App (Frontend)
> Requires Node.js, Expo CLI, and a phone with Expo Go or an emulator.

```bash
cd mobile-app
npm install
npx expo start
```

Scan the QR code from your terminal using the **Expo Go app** or run on an emulator.

---
