import NetInfo from '@react-native-community/netinfo';
import { useEffect, useState } from 'react';
import axios from 'axios';
import { getApiUrl } from './api'; // assuming getApiUrl is defined in utils/api.js

export const useNetworkStatus = () => {
  const [isConnected, setIsConnected] = useState(null);
  const [apiResponsive, setApiResponsive] = useState(false);

  useEffect(() => {
    const unsubscribe = NetInfo.addEventListener(state => {
      setIsConnected(state.isConnected);
    });

    return () => unsubscribe();
  }, []);

  useEffect(() => {
    const checkApi = async () => {
      try {
        const url = await getApiUrl();
        const response = await axios.get(`${url}/symbols`);
        setApiResponsive(response.status === 200);
      } catch (error) {
        setApiResponsive(false);
      }
    };

    if (isConnected) {
      checkApi();
    } else {
      setApiResponsive(false);
    }
  }, [isConnected]);

  return { isConnected, apiResponsive };
};
