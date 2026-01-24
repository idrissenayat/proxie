import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import HomeScreen from './src/screens/HomeScreen';
import CreateRequestScreen from './src/screens/CreateRequestScreen';
import OffersScreen from './src/screens/OffersScreen';
import BookingConfirmScreen from './src/screens/BookingConfirmScreen';
import ProviderDashboard from './src/screens/ProviderDashboard';
import RequestDetailScreen from './src/screens/RequestDetailScreen';
import SubmitOfferScreen from './src/screens/SubmitOfferScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
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
  );
}
