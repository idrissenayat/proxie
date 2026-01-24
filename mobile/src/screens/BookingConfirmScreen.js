import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { COLORS } from '../constants/colors';
import Header from '../components/Header';
import Card from '../components/Card';
import Button from '../components/Button';

const BookingConfirmScreen = ({ navigation, route }) => {
    const { booking } = route.params;

    return (
        <View style={styles.container}>
            <Header title="Confirmed" />
            <View style={styles.content}>
                <View style={styles.iconContainer}>
                    <Text style={styles.check}>✓</Text>
                </View>
                <Text style={styles.title}>Booking Confirmed!</Text>
                <Text style={styles.subtitle}>You're all set.</Text>

                <Card style={styles.detailsCard}>
                    <Text style={styles.label}>Service</Text>
                    <Text style={styles.value}>{booking.service_name}</Text>

                    <Text style={styles.label}>Date & Time</Text>
                    {/* Handle datetime formatting safely */}
                    <Text style={styles.value}>{booking.scheduled_date} @ {booking.scheduled_start}</Text>

                    <Text style={styles.label}>Price</Text>
                    <Text style={styles.priceValue}>${booking.price}</Text>

                    <Text style={styles.label}>Booking ID</Text>
                    <Text style={styles.smallValue}>{booking.id}</Text>
                </Card>

                <Button
                    title="Done"
                    onPress={() => navigation.navigate('Home')}
                    style={{ marginTop: 24 }}
                />
            </View>
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: COLORS.white,
    },
    content: {
        padding: 24,
        alignItems: 'center',
        flex: 1,
    },
    iconContainer: {
        width: 80,
        height: 80,
        borderRadius: 40,
        backgroundColor: COLORS.success,
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 24,
        marginTop: 40,
    },
    check: {
        color: COLORS.white,
        fontSize: 40,
        fontWeight: 'bold',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.text,
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: COLORS.textLight,
        marginBottom: 32,
    },
    detailsCard: {
        width: '100%',
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
    priceValue: {
        fontSize: 24,
        fontWeight: 'bold',
        color: COLORS.success,
    },
    smallValue: {
        fontSize: 14,
        color: COLORS.text,
        fontFamily: Platform.OS === 'ios' ? 'Courier' : 'monospace',
    },
});

export default BookingConfirmScreen;
