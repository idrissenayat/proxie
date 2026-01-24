import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { COLORS } from '../constants/colors';
import Header from '../components/Header';
import Button from '../components/Button';
import Card from '../components/Card';

const RequestDetailScreen = ({ navigation, route }) => {
    const { request } = route.params;

    return (
        <View style={styles.container}>
            <Header title="Request Details" showBack />
            <ScrollView contentContainerStyle={styles.content}>
                <Card>
                    <Text style={styles.label}>Service</Text>
                    <Text style={styles.value}>{request.service_type}</Text>

                    <Text style={styles.label}>Description</Text>
                    <Text style={styles.body}>{request.raw_input}</Text>

                    <Text style={styles.label}>Location</Text>
                    <Text style={styles.value}>{request.location?.city}</Text>

                    <Text style={styles.label}>Budget</Text>
                    <Text style={styles.price}>${request.budget?.min} - ${request.budget?.max}</Text>
                </Card>

                <Button
                    title="Make an Offer"
                    onPress={() => navigation.navigate('SubmitOffer', { request })}
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
        fontSize: 14,
        color: COLORS.textLight,
        marginTop: 12,
    },
    value: {
        fontSize: 18,
        fontWeight: '600',
        color: COLORS.text,
    },
    body: {
        fontSize: 16,
        color: COLORS.text,
        marginTop: 4,
        lineHeight: 22,
    },
    price: {
        fontSize: 20,
        fontWeight: 'bold',
        color: COLORS.success,
    },
});

export default RequestDetailScreen;
