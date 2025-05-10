import React, { useEffect, useState } from 'react';
import { View, Text, ScrollView, TextInput, Alert } from 'react-native';
import { fetchSymbols, fetchNewsEvents, addNewsEvent, deleteNewsEvent } from '../api/api';
import { SectionTitle } from '../components/SectionTitle';
import { Card } from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';

export default function NewsEventsScreen() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('XAUUSD');
  const [events, setEvents] = useState([]);
  const [eventName, setEventName] = useState('');
  const [eventTime, setEventTime] = useState(''); // Format: 'YYYY-MM-DD HH:MM:SS'

  const loadSymbols = async () => {
    const res = await fetchSymbols();
    if (res.status === 'success') setSymbols(res.symbols);
  };

  const loadEvents = async () => {
    const res = await fetchNewsEvents(selectedSymbol);
    if (res.status === 'success') setEvents(res.news_events);
  };

  useEffect(() => {
    loadSymbols();
    loadEvents();
  }, [selectedSymbol]);

  const handleAdd = async () => {
    if (!eventName || !eventTime) return Alert.alert('Error', 'Please enter both name and time');
    const res = await addNewsEvent(selectedSymbol, { event_name: eventName, event_time: eventTime });
    if (res.status === 'success') {
      setEventName('');
      setEventTime('');
      loadEvents();
    } else {
      Alert.alert('Error', res.message);
    }
  };

  const handleDelete = async (id) => {
    const res = await deleteNewsEvent(selectedSymbol, id);
    if (res.status === 'success') loadEvents();
  };

  return (
    <ScrollView className="p-4 space-y-4">
      <SectionTitle title="News Events" />
      <Text className="text-sm">Select Symbol</Text>
      <TextInput
        value={selectedSymbol}
        onChangeText={setSelectedSymbol}
        className="border p-2 rounded bg-white"
        autoCapitalize="characters"
      />

      <View className="space-y-2">
        <Text className="text-sm font-semibold">Add News Event</Text>
        <TextInput
          placeholder="Event Name"
          value={eventName}
          onChangeText={setEventName}
          className="border p-2 rounded bg-white"
        />
        <TextInput
          placeholder="YYYY-MM-DD HH:MM:SS"
          value={eventTime}
          onChangeText={setEventTime}
          className="border p-2 rounded bg-white"
        />
        <PrimaryButton title="Add Event" onPress={handleAdd} />
      </View>

      <SectionTitle title="Upcoming Events" />
      {events.map((e) => (
        <Card key={e.id}>
          <Text className="text-sm font-medium">{e.event_name}</Text>
          <Text className="text-xs text-gray-500">{e.event_time}</Text>
          <PrimaryButton title="Delete" onPress={() => handleDelete(e.id)} />
        </Card>
      ))}
    </ScrollView>
  );
}
