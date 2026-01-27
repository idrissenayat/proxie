import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function App() {
    console.log("Web App (App.web.js) is initializing...");
    return (
        <View style={styles.container}>
            <Text style={styles.title}>Proxie</Text>
            <Text style={styles.subtitle}>Web Portal Under Construction</Text>
            <Text style={styles.hint}>Please use the iOS/Android app for full functionality.</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh',
        width: '100vw',
    },
    title: {
        fontSize: 32,
        fontWeight: 'bold',
        marginBottom: 16,
        color: '#333',
    },
    subtitle: {
        fontSize: 18,
        color: '#666',
        marginBottom: 8,
    },
    hint: {
        fontSize: 14,
        color: '#999',
    },
});
