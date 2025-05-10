// components/Card.js
import React from 'react';
import { View, Text } from 'react-native';

const Card = ({ title, children }) => {
  return (
    <View
      style={{
        backgroundColor: 'white',
        borderRadius: 8,
        padding: 16,
        marginBottom: 16,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
        elevation: 5,
      }}
    >
      {title && (
        <Text style={{ fontSize: 18, fontWeight: 'bold', marginBottom: 8 }}>
          {title}
        </Text>
      )}
      {children}
    </View>
  );
};

export default Card;
