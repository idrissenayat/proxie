import React from 'react';
import { View, Text, StyleSheet, Image } from 'react-native';
import { COLORS } from '../constants/colors';
import Button from '../components/Button';

const HomeScreen = ({ navigation }) => {
    return (
        <View style={styles.container}>
            <View style={styles.content}>
                <View style={styles.logoContainer}>
                    {/* Placeholder for Logo */}
                    <View style={styles.logoPlaceholder} />
                    <Text style={styles.title}>Proxie</Text>
                    <Text style={styles.tagline}>Your craft, represented</Text>
                </View>

                <View style={styles.actions}>
                    <Button
                        title="I need a service"
                        onPress={() => navigation.navigate('CreateRequest')}
                    />
                    <Button
                        title="I'm a provider"
                        onPress={() => navigation.navigate('ProviderDashboard')}
                        type="secondary"
                    />
                </View>
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
        flex: 1,
        padding: 24,
        justifyContent: 'center',
    },
    logoContainer: {
        alignItems: 'center',
        marginBottom: 60,
    },
    logoPlaceholder: {
        width: 80,
        height: 80,
        backgroundColor: COLORS.primary,
        borderRadius: 20,
        marginBottom: 24,
        opacity: 0.2,
    },
    title: {
        fontSize: 40,
        fontWeight: 'bold',
        color: COLORS.primary,
        marginBottom: 8,
    },
    tagline: {
        fontSize: 18,
        color: COLORS.textLight,
    },
    actions: {
        gap: 16,
    },
});

export default HomeScreen;
