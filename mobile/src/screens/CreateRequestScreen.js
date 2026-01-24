import React, { useState } from 'react';
import { View, Text, StyleSheet, TextInput, ScrollView, Alert } from 'react-native';
import { COLORS } from '../constants/colors';
import Header from '../components/Header';
import Button from '../components/Button';
import { createRequest } from '../api/client';
import { v4 as uuidv4 } from 'uuid'; // React Native doesn't have crypto.randomUUID usually available without polyfill or libs.
// However, 'uuid' package wasn't installed. 
// Standard workaround for quick prototypes: generate random string.

const generateUUID = () => {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
        var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
};

const CreateRequestScreen = ({ navigation }) => {
    const [description, setDescription] = useState('');
    const [city, setCity] = useState('');
    const [budgetMin, setBudgetMin] = useState('');
    const [budgetMax, setBudgetMax] = useState('');
    const [loading, setLoading] = useState(false);

    const handleCreate = async () => {
        if (!description || !city) {
            Alert.alert('Error', 'Please describe your need and location');
            return;
        }

        setLoading(true);
        try {
            const consumerId = generateUUID(); // In real app, this comes from auth
            const payload = {
                consumer_id: consumerId,
                raw_input: description,
                service_category: "general", // MVP simplification
                service_type: "general",    // MVP simplification, ideally parsed or selected
                requirements: {
                    specializations: [],
                    description: description
                },
                location: {
                    city: city
                },
                timing: {},
                budget: {
                    min: parseFloat(budgetMin) || 0,
                    max: parseFloat(budgetMax) || 0,
                    currency: "USD"
                }
            };

            const response = await createRequest(payload);
            navigation.navigate('Offers', { requestId: response.data.id });
        } catch (error) {
            console.error(error);
            Alert.alert('Error', 'Failed to create request');
        } finally {
            setLoading(false);
        }
    };

    return (
        <View style={styles.container}>
            <Header title="New Request" showBack />
            <ScrollView contentContainerStyle={styles.content}>
                <Text style={styles.label}>What do you need?</Text>
                <TextInput
                    style={[styles.input, styles.textArea]}
                    multiline
                    placeholder="e.g. I need a haircut for curly hair..."
                    value={description}
                    onChangeText={setDescription}
                />

                <Text style={styles.label}>Location (City)</Text>
                <TextInput
                    style={styles.input}
                    placeholder="e.g. Brooklyn"
                    value={city}
                    onChangeText={setCity}
                />

                <Text style={styles.label}>Budget Range ($)</Text>
                <View style={styles.row}>
                    <TextInput
                        style={[styles.input, { flex: 1 }]}
                        placeholder="Min"
                        keyboardType="numeric"
                        value={budgetMin}
                        onChangeText={setBudgetMin}
                    />
                    <View style={{ width: 16 }} />
                    <TextInput
                        style={[styles.input, { flex: 1 }]}
                        placeholder="Max"
                        keyboardType="numeric"
                        value={budgetMax}
                        onChangeText={setBudgetMax}
                    />
                </View>

                <Button
                    title="Find Providers"
                    onPress={handleCreate}
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

export default CreateRequestScreen;
