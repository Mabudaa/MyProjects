// App.js
import React, { useState, useEffect } from 'react';
import { NavigationContainer, DefaultTheme, DarkTheme } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';

import SymbolsScreen from './screens/SymbolsScreen';
import SymbolDetailScreen from './screens/SymbolDetailScreen';
import EditSymbolsScreen from './screens/EditSymbolsScreen';
import EditNewsScreen from './screens/EditNewsScreen';
import EquityCurveScreen from './screens/EquityCurveScreen';
import OpenTradesScreen from './screens/OpenTradesScreen';
import SettingsScreen from './screens/SettingsScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const SymbolsStack = () => (
  <Stack.Navigator>
    <Stack.Screen name="SymbolsMain" component={SymbolsScreen} options={{ title: 'Symbols Dashboard' }} />
    <Stack.Screen name="SymbolDetail" component={SymbolDetailScreen} options={{ title: 'Symbol Details' }} />
  </Stack.Navigator>
);

export default function App() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    AsyncStorage.getItem('theme').then((theme) => {
      setIsDarkMode(theme === 'dark');
    });
  }, []);

  const toggleTheme = async () => {
    const newTheme = isDarkMode ? 'light' : 'dark';
    await AsyncStorage.setItem('theme', newTheme);
    setIsDarkMode(!isDarkMode);
  };

  return (
    <NavigationContainer theme={isDarkMode ? DarkTheme : DefaultTheme}>
      <Tab.Navigator
        screenOptions={({ route }) => ({
          headerShown: false,
          tabBarIcon: ({ color, size }) => {
            let iconName;
            if (route.name === 'Dashboard') iconName = 'home';
            else if (route.name === 'EditSymbols') iconName = 'construct';
            else if (route.name === 'EditNews') iconName = 'newspaper';
            else if (route.name === 'EquityCurve') iconName = 'analytics';
            else if (route.name === 'OpenTrades') iconName = 'briefcase';
            else if (route.name === 'Settings') iconName = 'settings';
            return <Ionicons name={iconName} size={size} color={color} />;
          },
          tabBarLabelStyle: { fontSize: 14 },
          tabBarActiveTintColor: '#007bff',
          tabBarInactiveTintColor: 'gray',
        })}
      >
        <Tab.Screen name="Dashboard" component={SymbolsStack} />
        <Tab.Screen name="EditSymbols" component={EditSymbolsScreen} options={{ title: 'Edit Symbols' }} />
        <Tab.Screen name="EditNews" component={EditNewsScreen} options={{ title: 'Edit News' }} />
        <Tab.Screen name="EquityCurve" component={EquityCurveScreen} />
        <Tab.Screen name="OpenTrades" component={OpenTradesScreen} />
        <Tab.Screen name="Settings">
          {() => <SettingsScreen toggleTheme={toggleTheme} isDarkMode={isDarkMode} />}
        </Tab.Screen>
      </Tab.Navigator>
    </NavigationContainer>
  );
}
