import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';

import DashboardScreen from './screens/DashboardScreen';
import SymbolsScreen from './screens/SymbolsScreen';
import SymbolDetailScreen from './screens/SymbolDetailScreen';
import EquityCurveScreen from './screens/EquityCurveScreen';
import NewsEventsScreen from './screens/NewsEventsScreen';
import SettingsScreen from './screens/SettingsScreen'; // Optional: for API URL settings

const Stack = createNativeStackNavigator();

const AppNavigation = () => {
  return (
    <NavigationContainer>
      <Stack.Navigator
        
        screenOptions={{
          headerShown: true,
          animation: 'slide_from_right',
        }}

      >
        <Stack.Screen name="Dashboard" component={DashboardScreen} />
        <Stack.Screen name="Symbols" component={SymbolsScreen} />
        <Stack.Screen name="SymbolDetails" component={SymbolDetailsScreen} />
        <Stack.Screen name="EquityCurve" component={EquityCurveScreen} />
        <Tab.Screen name="OpenTrades" component={OpenTradesScreen} />
        <Stack.Screen name="NewsEvents" component={NewsEventsScreen} />
        <Stack.Screen name="Settings" component={SettingsScreen} />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default AppNavigation;
