import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, ScrollView, Alert } from 'react-native';
import { COLORS } from '../constants/colors';
import Header from '../components/Header';
import Button from '../components/Button';
import { submitOffer } from '../api/client';
import { v4 as uuidv4 } from 'uuid'; // Workaround function needed again or shared util

// Simplify for now, duplicate helper
const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
};

const SubmitOfferScreen = ({ navigation, route }) => {
    const { request } = route.params;

    const [price, setPrice] = useState('');
    const [message, setMessage] = useState('');
    const [date, setDate] = useState('2026-05-20');
    const [startTime, setStartTime] = useState('10:00');
    const [endTime, setEndTime] = useState('11:00');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async () => {
        if (!price) {
            Alert.alert('Error', 'Please enter a price');
            return;
        }

        setLoading(true);
        try {
            // Mock Provider ID or fetch from storage
            const providerId = "test-provider-id";
            // Also need a service_id. In real flow, pick one of provider's services.
            // We'll generate one or use null if backend allows (schema says optional? No, provider.py model might need it?)
            // offers.py router: service_id=offer.service_id. `Offer` model has it.
            // We'll generate a dummy ID.

            const payload = {
                request_id: request.id,
                provider_id: providerId,
                service_id: generateUUID(),
                service_name: request.service_type,
                available_slots: [
                    {
                        date: date,
                        start_time: startTime,
                        end_time: endTime
                    }
                ],
                price: parseFloat(price),
                currency: "USD",
                message: message
            };

            await submitOffer(payload);
            Alert.alert('Success', 'Offer sent!', [
                { text: 'OK', onPress: () => navigation.popToTop() }
            ]);
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'Failed to send offer');
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            <Header title="Submit Offer" showBack />
            <ScrollView contentContainerStyle={styles.content}>
                <Text style={styles.label}>Your Price ($)</Text>
                <TextInput
                    style={styles.input}
                    keyboardType="numeric"
                    value={price}
                    onChangeText={setPrice}
                    placeholder="0.00"
                />

                <Text style={styles.label}>Available Slot</Text>
                <View style={styles.row}>
                    <TextInput style={[styles.input, { flex: 2 }]} value={date} onChangeText={setDate} placeholder="YYYY-MM-DD" />
                    <View style={{ width: 8 }} />
                    <TextInput style={[styles.input, { flex: 1 }]} value={startTime} onChangeText={setStartTime} placeholder="HH:MM" />
                    <Text style={{ alignSelf: 'center', marginHorizontal: 4 }}>-</Text>
                    <TextInput style={[styles.input, { flex: 1 }]} value={endTime} onChangeText={setEndTime} placeholder="HH:MM" />
                </View>

                <Text style={styles.label}>Message</Text>
                <TextInput
                    style={[styles.input, styles.textArea]}
                    multiline
                    placeholder="Add a note..."
                    value={message}
                    onChangeText={setMessage}
                />

                <Button
                    title="Submit Offer"
                    onPress={handleSubmit}
                    loading={loading}
                    style={{ marginTop: 24 }}
                />
            </ScrollView>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.gray,
    },
    content: {
        padding: 16,
    },
    label: {
        fontSize: 16,
        fontWeight: '600',
        color: COLORS.text,
        marginBottom: 8,
        marginTop: 16,
    },
    input: {
        backgroundColor: COLORS.white,
        padding: 12,
        borderRadius: 8,
        borderWidth: 1,
        borderColor: COLORS.border,
        fontSize: 16,
    },
    textArea: {
        height: 100,
        textAlignVertical: 'top',
    },
    row: {
        flexDirection: 'row',
    },
});

export default SubmitOfferScreen;
