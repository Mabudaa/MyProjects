// screens/OpenTradesScreen.js
import React, { useEffect, useState } from 'react'
import { View, Text, ScrollView, ActivityIndicator } from 'react-native'
import { fetchOpenTrades } from '../api/api'
import { SectionTitle } from '../components/SectionTitle'
import { Card } from '../components/Card'

export default function OpenTradesScreen() {
  const [loading, setLoading] = useState(true)
  const [tradeGroups, setTradeGroups] = useState({})

  useEffect(() => {
    const loadTrades = async () => {
      setLoading(true)
      const res = await fetchOpenTrades()
      setTradeGroups(res)
      setLoading(false)
    }

    loadTrades()
  }, [])

  if (loading) return <ActivityIndicator size="large" className="mt-10" />

  return (
    <ScrollView className="p-4 space-y-4">
      <SectionTitle title="Open Trades" />

      {Object.entries(tradeGroups).map(([timeframe, trades]) => (
        <View key={timeframe} className="space-y-2">
          <Text className="text-base font-semibold">{timeframe}</Text>
          {trades.map((trade, idx) => (
            <Card key={idx}>
              <Text className="text-sm font-medium">{trade.symbol}</Text>
              <Text className="text-xs text-gray-500">
                Volume: {trade.volume} | Price: {trade.price} | Profit: {trade.profit}
              </Text>
              <Text className="text-xs text-gray-400">Comment: {trade.comment}</Text>
            </Card>
          ))}
        </View>
      ))}
    </ScrollView>
  )
}
