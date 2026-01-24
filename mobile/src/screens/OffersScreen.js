import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, FlatList, Alert } from 'react-native';
import { COLORS } from '../constants/colors';
import Header from '../components/Header';
import Card from '../components/Card';
import Button from '../components/Button';
import { getOffers, acceptOffer } from '../api/client';

const OffersScreen = ({ navigation, route }) => {
    const { requestId } = route.params;
    const [offers, setOffers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [accepting, setAccepting] = useState(null);

    useEffect(() => {
        fetchOffers();
        // Poll for offers every 5 seconds for MVP demo experience
        const interval = setInterval(fetchOffers, 5000);
        return () => clearInterval(interval);
    }, [requestId]);

    const fetchOffers = async () => {
        try {
            const response = await getOffers(requestId);
            setOffers(response.data);
        } catch (error) {
            console.log('Error fetching offers', error);
        } finally {
            setLoading(false);
        }
    };

    const handleAccept = async (offer) => {
        setAccepting(offer.id);
        try {
            // Assuming first slot for MVP as discussed
            // const slot = offer.available_slots && offer.available_slots[0];
            // if (!slot) throw new Error("No slots");

            // Update: Backend REST API currently ignores body, but we pass it anyway.
            // And backend (Step 203) picks first slot automatically if not provided or just picks first slot regardless.
            // So simple call is fine.

            const response = await acceptOffer(offer.id, {});
            navigation.navigate('BookingConfirm', { booking: response.data });
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'Failed to accept offer');
        } finally {
            setAccepting(null);
        }
    };

    const renderOffer = ({ item }) => (
        <Card>
            <View style={styles.offerHeader}>
                <Text style={styles.serviceName}>{item.service_name}</Text>
                <Text style={styles.price}>${item.price}</Text>
            </View>
            <Text style={styles.providerName}>Provider ID: {item.provider_id.substring(0, 8)}...</Text>

            <Text style={styles.slotsLabel}>Available Slots:</Text>
            {item.available_slots && item.available_slots.map((slot, idx) => (
                <Text key={idx} style={styles.slotText}>
                    {slot.date} @ {slot.start_time}
                </Text>
            ))}

            {item.message && (
                <Text style={styles.message}>"{item.message}"</Text>
            )}

            <Button
                title="Accept Offer"
                onPress={() => handleAccept(item)}
                loading={accepting === item.id}
                style={{ marginTop: 12 }}
            />
        </Card>
    );

    return (
        <View style={styles.container}>
            <Header title="Offers" showBack />
            <View style={styles.content}>
                {loading ? (
                    <Text style={styles.status}>Finding skilled providers...</Text>
                ) : (
                    <FlatList
                        data={offers}
                        renderItem={renderOffer}
                        keyExtractor={item => item.id}
                        ListEmptyComponent={
                            <Text style={styles.empty}>No offers yet. Waiting for providers...</Text>
                        }
                    />
                )}
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.gray,
    },
    content: {
        flex: 1,
        padding: 16,
    },
    status: {
        textAlign: 'center',
        marginTop: 20,
        fontSize: 16,
        color: COLORS.textLight,
    },
    empty: {
        textAlign: 'center',
        marginTop: 40,
        fontSize: 16,
        color: COLORS.textLight,
    },
    offerHeader: {
        flexDirection: 'row',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 8,
    },
    serviceName: {
        fontSize: 18,
        fontWeight: 'bold',
        color: COLORS.text,
    },
    price: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.success,
    },
    providerName: {
        fontSize: 14,
        color: COLORS.textLight,
        marginBottom: 8,
    },
    slotsLabel: {
        fontWeight: '600',
        marginTop: 8,
        marginBottom: 4,
    },
    slotText: {
        fontSize: 14,
        color: COLORS.text,
    },
    message: {
        fontStyle: 'italic',
        color: COLORS.text,
        marginVertical: 12,
        padding: 8,
        backgroundColor: COLORS.gray,
        borderRadius: 8,
    },
});

export default OffersScreen;
