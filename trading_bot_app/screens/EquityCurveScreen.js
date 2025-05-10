// screens/EquityCurveScreen.js
import React, { useEffect, useState } from 'react'
import { View, Text, FlatList, ActivityIndicator } from 'react-native'
import { fetchEquityCurve } from '../api/api'
import  SectionTitle  from '../components/SectionTitle'
import  Card  from '../components/Card'

export default function EquityCurveScreen() {
  const [equity, setEquity] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const loadEquity = async () => {
      setLoading(true)
      const data = await fetchEquityCurve()
      setEquity(data)
      setLoading(false)
    }

    loadEquity()
  }, [])

  return (
    <View className="p-4">
      <SectionTitle title="Equity Curve" />
      {loading ? (
        <ActivityIndicator size="large" />
      ) : (
        <FlatList
          data={equity}
          keyExtractor={(item, index) => index.toString()}
          renderItem={({ item }) => (
            <Card>
              <Text className="text-base">Equity: ${item.equity.toFixed(2)}</Text>
              <Text className="text-sm text-gray-500">
                {new Date(item.timestamp).toLocaleString()}
              </Text>
            </Card>
          )}
        />
      )}
    </View>
  )
}
