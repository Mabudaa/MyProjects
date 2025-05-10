import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator, TextInput } from 'react-native';
import { fetchSymbols, fetchOpenTrades, toggleSymbol, fetchNewsEvents, addNewsEvent } from '../api/api';
import SectionTitle from '../components/SectionTitle';
import Card from '../components/Card';
import PrimaryButton from '../components/PrimaryButton';

export default function SymbolDetailsScreen({ route, navigation }) {
  const { symbol } = route.params; // Symbol passed from SymbolScreen
  const [openTrades, setOpenTrades] = useState([]);
  const [loading, setLoading] = useState(false);
  const [symbolDetails, setSymbolDetails] = useState(symbol);
  const [newsEvents, setNewsEvents] = useState([]);
  const [newEvent, setNewEvent] = useState('');
  const [eventSubmitting, setEventSubmitting] = useState(false);

  useEffect(() => {
    const loadOpenTrades = async () => {
      setLoading(true);
      const response = await fetchOpenTrades();
      if (Array.isArray(response.trades)) {
        setOpenTrades(response.trades.filter(trade => trade.symbol === symbol.name)); // Filter trades by symbol
      }
      setLoading(false);
    };

    const loadNewsEvents = async () => {
      setLoading(true);
      const response = await fetchNewsEvents(symbol.name);
      if (Array.isArray(response.events)) {
        setNewsEvents(response.events);
      }
      setLoading(false);
    };

    loadOpenTrades();
    loadNewsEvents();
  }, [symbol]);

  const handleToggle = async () => {
    await toggleSymbol(symbol.name);
    // Update the symbol state
    setSymbolDetails((prevDetails) => ({
      ...prevDetails,
      active: !prevDetails.active,
    }));
  };

  const handleAddEvent = async () => {
    if (!newEvent) return;

    setEventSubmitting(true);
    await addNewsEvent(symbol.name, { event: newEvent });
    setNewEvent('');
    setEventSubmitting(false);
    // Refresh news events
    loadNewsEvents();
  };

  const groupTradesByTimeFrame = (trades) => {
    return trades.reduce((acc, trade) => {
      const timeframe = trade.timeframe || 'Unknown Timeframe'; // Assuming `timeframe` is in each trade object
      if (!acc[timeframe]) {
        acc[timeframe] = [];
      }
      acc[timeframe].push(trade);
      return acc;
    }, {});
  };

  const groupedTrades = groupTradesByTimeFrame(openTrades);

  return (
    <ScrollView contentContainerStyle={{ padding: 16 }}>
      <SectionTitle title={`${symbol.name} Details`} />
      <Card>
        <Text style={{ fontSize: 18, fontWeight: 'bold' }}>Symbol: {symbol.name}</Text>
        <Text style={{ fontSize: 16 }}>Digits: {symbol.digits}</Text>
        <Text style={{ fontSize: 16 }}>Contract Size: {symbol.contract_size}</Text>
      </Card>

      <PrimaryButton
        title={symbolDetails.active ? 'Deactivate Symbol' : 'Activate Symbol'}
        onPress={handleToggle}
        style={{ marginVertical: 20 }}
      />

      <SectionTitle title="Open Trades by Timeframe" />
      {loading ? (
        <ActivityIndicator size="large" color="#007bff" />
      ) : (
        Object.keys(groupedTrades).map((timeframe) => (
          <View key={timeframe} style={{ marginBottom: 20 }}>
            <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 10 }}>
              {timeframe}
            </Text>
            {groupedTrades[timeframe].map((trade, index) => (
              <Card key={index} style={{ marginBottom: 10 }}>
                <Text style={{ fontSize: 16 }}>Entry Price: {trade.price_open}</Text>
                <Text style={{ fontSize: 16 }}>Volume: {trade.volume}</Text>
                <Text style={{ fontSize: 16 }}>
                  Open Time: {new Date(trade.open_time).toLocaleString()}
                </Text>
              </Card>
            ))}
          </View>
        ))
      )}

      <SectionTitle title="News Events" />
      <View style={{ marginBottom: 20 }}>
        {newsEvents.length === 0 ? (
          <Text>No news events for this symbol.</Text>
        ) : (
          newsEvents.map((event, index) => (
            <Card key={index} style={{ marginBottom: 10 }}>
              <Text style={{ fontSize: 16 }}>{event.event}</Text>
            </Card>
          ))
        )}
      </View>

      <SectionTitle title="Add New Event" />
      <View style={{ marginBottom: 20 }}>
        <TextInput
          value={newEvent}
          onChangeText={setNewEvent}
          placeholder="Enter event description"
          style={{
            borderWidth: 1,
            borderColor: '#ccc',
            padding: 10,
            borderRadius: 5,
            marginBottom: 10,
            fontSize: 16,
          }}
        />
        <PrimaryButton
          title={eventSubmitting ? 'Submitting...' : 'Add Event'}
          onPress={handleAddEvent}
          disabled={eventSubmitting}
        />
      </View>
    </ScrollView>
  );
}
