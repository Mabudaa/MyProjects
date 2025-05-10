// components/SectionTitle.js
import React from 'react';
import { Text } from 'react-native';

const SectionTitle = ({ children }) => {
  return (
    <Text
      style={{
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 16,
        color: '#333',
      }}
    >
      {children}
    </Text>
  );
};

export default SectionTitle;
