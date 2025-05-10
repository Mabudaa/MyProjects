import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, TouchableOpacity, ScrollView } from 'react-native';
import { fetchSymbols, addNewsEvent } from '../api/api';
import SectionTitle from '../components/SectionTitle';
import PrimaryButton from '../components/PrimaryButton';

export default function EditNewsScreen() {
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbols, setSelectedSymbols] = useState([]);
  const [newsEvent, setNewsEvent] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadSymbols = async () => {
      setLoading(true);
      const response = await fetchSymbols();
      if (Array.isArray(response.symbols)) {
        setSymbols(response.symbols);
      }
      setLoading(false);
    };

    loadSymbols();
  }, []);

  const handleToggleSymbol = (symbol) => {
    setSelectedSymbols((prevSelected) =>
      prevSelected.includes(symbol)
        ? prevSelected.filter((item) => item !== symbol)
        : [...prevSelected, symbol]
    );
  };

  const handleSubmit = async () => {
    if (!newsEvent || selectedSymbols.length === 0) return;

    setLoading(true);
    for (const symbol of selectedSymbols) {
      await addNewsEvent(symbol, { event: newsEvent });
    }
    setLoading(false);
    setNewsEvent('');
    setSelectedSymbols([]);
  };

  return (
    <ScrollView contentContainerStyle={{ padding: 16 }}>
      <SectionTitle title="Add News Event" />
      <TextInput
        style={{
          height: 40,
          borderColor: 'gray',
          borderWidth: 1,
          marginBottom: 16,
          paddingHorizontal: 8,
        }}
        placeholder="News Event Description"
        value={newsEvent}
        onChangeText={setNewsEvent}
      />
      <Text style={{ fontSize: 16, marginBottom: 8 }}>Select Symbols</Text>
      <View>
        {symbols.map((symbol) => (
          <TouchableOpacity
            key={symbol.name}
            onPress={() => handleToggleSymbol(symbol.name)}
            style={{
              flexDirection: 'row',
              alignItems: 'center',
              paddingVertical: 8,
            }}
          >
            <Text style={{ fontSize: 16, marginRight: 10 }}>{symbol.name}</Text>
            {selectedSymbols.includes(symbol.name) && (
              <Text style={{ fontSize: 16, color: 'green' }}>Selected</Text>
            )}
          </TouchableOpacity>
        ))}
      </View>
      <PrimaryButton
        title="Save News Event"
        onPress={handleSubmit}
        disabled={loading || !newsEvent || selectedSymbols.length === 0}
      />
    </ScrollView>
  );
}
