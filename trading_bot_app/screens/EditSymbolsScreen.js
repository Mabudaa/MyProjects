import React, { useState, useEffect } from 'react';
import { View, Text, TextInput, FlatList, ActivityIndicator, Alert } from 'react-native';
import { fetchSymbols, addSymbol, deleteSymbol } from '../api/api';
import SectionTitle from '../components/SectionTitle';
import Card from '../components/Card';
import PrimaryButton from '../components/PrimaryButton';
import { useIsFocused } from '@react-navigation/native';

export default function EditSymbolsScreen() {
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newSymbol, setNewSymbol] = useState({ name: '', digits: '', contract_size: '' });
  const isFocused = useIsFocused();

  const loadSymbols = async () => {
    setLoading(true);
    try {
      const res = await fetchSymbols();
      if (Array.isArray(res.symbols)) setSymbols(res.symbols);
    } catch (error) {
      console.error(error);
      Alert.alert('Error', 'Failed to load symbols');
    }
    setLoading(false);
  };

  const handleAdd = async () => {
    if (!newSymbol.name || !newSymbol.digits || !newSymbol.contract_size) return;
    try {
      await addSymbol({
        name: newSymbol.name,
        digits: parseFloat(newSymbol.digits),
        contract_size: parseInt(newSymbol.contract_size),
      });
      setNewSymbol({ name: '', digits: '', contract_size: '' });
      loadSymbols();
    } catch (error) {
      Alert.alert('Error', 'Failed to add symbol');
    }
  };

  const handleDelete = async (symbol) => {
    Alert.alert('Delete Symbol', `Are you sure you want to delete ${symbol}?`, [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Delete',
        style: 'destructive',
        onPress: async () => {
          try {
            await deleteSymbol(symbol);
            loadSymbols();
          } catch (error) {
            Alert.alert('Error', 'Failed to delete symbol');
          }
        },
      },
    ]);
  };

  useEffect(() => {
    if (isFocused) loadSymbols();
  }, [isFocused]);

  return (
    <View className="p-4">
      <SectionTitle text="Add Symbol" />
      <View className="mb-4">
        <TextInput
          placeholder="Name"
          value={newSymbol.name}
          onChangeText={(text) => setNewSymbol({ ...newSymbol, name: text })}
          className="border p-2 rounded mb-2 text-base"
        />
        <TextInput
          placeholder="Digits"
          value={newSymbol.digits}
          onChangeText={(text) => setNewSymbol({ ...newSymbol, digits: text })}
          keyboardType="numeric"
          className="border p-2 rounded mb-2 text-base"
        />
        <TextInput
          placeholder="Contract Size"
          value={newSymbol.contract_size}
          onChangeText={(text) => setNewSymbol({ ...newSymbol, contract_size: text })}
          keyboardType="numeric"
          className="border p-2 rounded mb-2 text-base"
        />
        <PrimaryButton title="Add Symbol" onPress={handleAdd} />
      </View>

      <SectionTitle text="Delete Symbols" />
      {loading ? (
        <ActivityIndicator size="large" color="#007bff" />
      ) : (
        <FlatList
          data={symbols}
          keyExtractor={(item) => item.name}
          renderItem={({ item }) => (
            <Card onPress={() => handleDelete(item.name)}>
              <Text className="text-base font-medium">{item.name}</Text>
              <Text className="text-sm text-gray-600">
                Digits: {item.digits} | Size: {item.contract_size}
              </Text>
              <Text className="text-sm text-red-600 mt-1">Tap to delete</Text>
            </Card>
          )}
        />
      )}
    </View>
  );
}
