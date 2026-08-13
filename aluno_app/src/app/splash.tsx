import React, { useEffect } from 'react';
import { StyleSheet, Text, View, ActivityIndicator, Image } from 'react-native';
import { LinearGradient } from 'expo-linear-gradient';
import { useRouter } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import logo from '../../assets/images/logo1-removebg-preview.png';

export default function SplashScreen() {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => {
      router.replace('/onboarding');
    }, 2500); // Redirect to Onboarding screen after 2.5 seconds

    return () => clearTimeout(timer);
  }, []);

  return (
    <LinearGradient
      colors={['#ffffff', '#ffffff']}
      style={styles.container}
      start={{ x: 0, y: 0 }}
      end={{ x: 1, y: 1 }}
    >
      <StatusBar style="dark" />
      <View style={styles.content}>
        {/* Logo Container */}
        <View style={styles.logoContainer}>
          <Image source={logo} style={styles.logo} resizeMode="contain" />
        </View>

        {/* Text Logo */}
        <View style={styles.textContainer}>
          <Text style={styles.title}>EdukAngola</Text>
          <Text style={styles.subtitle}>EDUCAÇÃO · ANGOLA</Text>
        </View>
      </View>

      {/* Blinking/Loading Indicator */}
      <View style={styles.indicatorContainer}>
        <ActivityIndicator size="small" color="#1a1a1a" />
      </View>
    </LinearGradient>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  content: {
    alignItems: 'center',
    gap: 22,
  },
  logoContainer: {
    width: 122,
    height: 122,
    borderRadius: 34,
    backgroundColor: 'rgba(0, 0, 0, 0.06)',
    borderWidth: 1,
    borderColor: 'rgba(0, 0, 0, 0.10)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  logo: {
    width: 80,
    height: 80,
  },
  textContainer: {
    alignItems: 'center',
  },
  title: {
    fontFamily: 'System',
    fontSize: 27,
    fontWeight: '800',
    color: '#1a1a1a',
    letterSpacing: -0.5,
  },
  subtitle: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: 'rgba(0, 0, 0, 0.5)',
    marginTop: 5,
    letterSpacing: 1.5,
  },
  indicatorContainer: {
    position: 'absolute',
    bottom: 50,
    flexDirection: 'row',
    gap: 8,
  },
});
