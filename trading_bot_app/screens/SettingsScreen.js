// screens/SettingsScreen.js
import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, StyleSheet, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import PrimaryButton  from '../components/PrimaryButton';

const SettingsScreen = () => {
  const [ipAddress, setIpAddress] = useState('');

  useEffect(() => {
    const loadIpAddress = async () => {
      try {
        const savedIp = await AsyncStorage.getItem('botIpAddress');
        if (savedIp) setIpAddress(savedIp);
      } catch (err) {
        console.error('Failed to load IP:', err);
      }
    };
    loadIpAddress();
  }, []);

  const handleSave = async () => {
    try {
      await AsyncStorage.setItem('botIpAddress', ipAddress);
      Alert.alert('Success', 'IP address saved successfully');
    } catch (err) {
      console.error('Failed to save IP:', err);
      Alert.alert('Error', 'Failed to save IP address');
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.label}>Trading Bot IP Address</Text>
      <TextInput
        style={styles.input}
        value={ipAddress}
        onChangeText={setIpAddress}
        placeholder="e.g. http://192.168.1.100:5000"
        autoCapitalize="none"
      />
      <PrimaryButton title="Save IP Address" onPress={handleSave} />
    </View>
  );
};

export default SettingsScreen;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#fff',
  },
  label: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  input: {
    borderWidth: 1,
    borderColor: '#ccc',
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
    marginBottom: 20,
  },
});
