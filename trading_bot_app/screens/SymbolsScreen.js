import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { fetchSymbols } from '../api/api';
import SectionTitle from '../components/SectionTitle';
import Card from '../components/Card';
import { PrimaryButton } from '../components/PrimaryButton';

export default function SymbolsScreen() {
  const [symbols, setSymbols] = useState([]);
  const [loading, setLoading] = useState(false);
  const navigation = useNavigation();

  const loadSymbols = async () => {
    setLoading(true);
    const response = await fetchSymbols();
    if (Array.isArray(response.symbols)) {
      setSymbols(response.symbols);
    }
    setLoading(false);
  };

  useEffect(() => {
    const unsubscribe = navigation.addListener('focus', loadSymbols);
    return unsubscribe;
  }, [navigation]);

  const renderItem = ({ item }) => (
    <Card>
      <TouchableOpacity onPress={() => navigation.navigate('SymbolDetail', { symbol: item.name })}>
        <Text className="text-xl font-bold">{item.name}</Text>
        <Text className="text-sm">Digits: {item.digits}</Text>
        <Text className="text-sm">Contract Size: {item.contract_size}</Text>
      </TouchableOpacity>

      <View className="flex-row mt-2 space-x-2">
        <PrimaryButton
          title="View Details"
          onPress={() => navigation.navigate('SymbolDetail', { symbol: item.name })}
        />
      </View>
    </Card>
  );

  return (
    <View className="flex-1 p-4">
      <SectionTitle title="Symbols Dashboard" />
      {loading ? (
        <ActivityIndicator size="large" color="#007bff" />
      ) : (
        <FlatList
          data={symbols}
          keyExtractor={(item) => item.name}
          renderItem={renderItem}
          contentContainerStyle={{ paddingBottom: 50 }}
        />
      )}
    </View>
  );
}
