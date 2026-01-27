import React from 'react';
import { View, Text } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { enableScreens } from 'react-native-screens';

// Disable native screens for web compatibility if needed
enableScreens(false);

import HomeScreen from './src/screens/HomeScreen';
import CreateRequestScreen from './src/screens/CreateRequestScreen';
import OffersScreen from './src/screens/OffersScreen';
import BookingConfirmScreen from './src/screens/BookingConfirmScreen';
import ProviderDashboard from './src/screens/ProviderDashboard';
import RequestDetailScreen from './src/screens/RequestDetailScreen';
import SubmitOfferScreen from './src/screens/SubmitOfferScreen';

const Stack = createNativeStackNavigator();

const linking = {
  prefixes: ['http://localhost:8081', 'exp://'],
  config: {
    screens: {
      Home: '',
      CreateRequest: 'create-request',
      Offers: 'offers',
      BookingConfirm: 'booking-confirm',
      ProviderDashboard: 'provider',
      RequestDetail: 'request/:id',
      SubmitOffer: 'submit-offer',
    },
  },
};

export default function App() {
  console.log("Native App is initializing...");
  return (
    <View style={{ flex: 1, height: '100%', width: '100%' }}>
      <SafeAreaProvider style={{ flex: 1 }}>
        <NavigationContainer linking={linking} fallback={<View><Text>Loading...</Text></View>}>
          <Stack.Navigator
            initialRouteName="Home"
            screenOptions={{ headerShown: false }}
          >
            <Stack.Screen name="Home" component={HomeScreen} />

            {/* Consumer Flow */}
            <Stack.Screen name="CreateRequest" component={CreateRequestScreen} />
            <Stack.Screen name="Offers" component={OffersScreen} />
            <Stack.Screen name="BookingConfirm" component={BookingConfirmScreen} />

            {/* Provider Flow */}
            <Stack.Screen name="ProviderDashboard" component={ProviderDashboard} />
            <Stack.Screen name="RequestDetail" component={RequestDetailScreen} />
            <Stack.Screen name="SubmitOffer" component={SubmitOfferScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      </SafeAreaProvider>
    </View>
  );
}
