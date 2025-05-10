// components/PrimaryButton.js
import React from 'react';
import { TouchableOpacity, Text } from 'react-native';

const PrimaryButton = ({ onPress, children, style }) => {
  return (
    <TouchableOpacity
      onPress={onPress}
      style={[
        { backgroundColor: '#4CAF50', padding: 12, borderRadius: 8 },
        style, // Allow additional styling via props
      ]}
    >
      <Text style={{ color: 'white', textAlign: 'center', fontWeight: 'bold' }}>
        {children}
      </Text>
    </TouchableOpacity>
  );
};

export default PrimaryButton;
