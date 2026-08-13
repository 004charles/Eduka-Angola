import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, Dimensions } from 'react-native';
import { useRouter } from 'expo-router';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';

const { width } = Dimensions.get('window');

const SLIDES = [
  {
    id: 1,
    icon: 'school-outline',
    title: 'Aprenda no seu ritmo',
    description: 'Aceda a cursos presenciais e em vídeo gravados pelos melhores centros de formação de Angola.',
  },
  {
    id: 2,
    icon: 'qrcode-scan',
    title: 'Certificados com QR Code',
    description: 'Conclua os seus cursos e receba certificados com validação pública instantânea. Modo offline e aulas em vídeo também incluídos.',
  },
  {
    id: 3,
    icon: 'cellphone-link',
    title: 'Estude em Qualquer Lugar',
    description: 'Descarregue as suas aulas em vídeo para continuar a aprender mesmo sem acesso à internet.',
  },
];

export default function OnboardingScreen() {
  const router = useRouter();
  const [activeSlide, setActiveSlide] = useState(0);

  const handleNext = () => {
    if (activeSlide < SLIDES.length - 1) {
      setActiveSlide(activeSlide + 1);
    } else {
      router.replace('/login');
    }
  };

  const handleSkip = () => {
    router.replace('/login');
  };

  const currentSlide = SLIDES[activeSlide];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      
      {/* Skip Button Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={handleSkip}>
          <Text style={styles.skipText}>Saltar</Text>
        </TouchableOpacity>
      </View>

      {/* Main Slide Content */}
      <View style={styles.slideContent}>
        {/* Rounded Illustration Box */}
        <View style={styles.illustrationContainer}>
          <MaterialCommunityIcons name={currentSlide.icon as any} size={88} color="#5B18E6" />
          <View style={styles.tagBadge}>
            <Text style={styles.tagText}>ilustração</Text>
          </View>
        </View>

        {/* Text Details */}
        <Text style={styles.title}>{currentSlide.title}</Text>
        <Text style={styles.description}>{currentSlide.description}</Text>
      </View>

      {/* Bottom Navigation Row */}
      <View style={styles.footer}>
        {/* Slide Indicator Dots */}
        <View style={styles.dotsContainer}>
          {SLIDES.map((_, index) => {
            const isActive = index === activeSlide;
            return (
              <View
                key={index}
                style={[
                  styles.dot,
                  isActive ? styles.activeDot : null,
                ]}
              />
            );
          })}
        </View>

        {/* Next/Arrow Action Button */}
        <TouchableOpacity style={styles.arrowButton} onPress={handleNext}>
          <MaterialCommunityIcons name="arrow-right" size={28} color="#ffffff" />
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
  header: {
    height: 48,
    flexDirection: 'row',
    justifyContent: 'flex-end',
    alignItems: 'center',
    paddingHorizontal: 26,
  },
  skipText: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '700',
    color: '#8B8598',
  },
  slideContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: 34,
    textAlign: 'center',
  },
  illustrationContainer: {
    width: 224,
    height: 224,
    borderRadius: 30,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  tagBadge: {
    position: 'absolute',
    bottom: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.75)',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 6,
  },
  tagText: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '600',
    color: '#7A6BA8',
  },
  title: {
    fontFamily: 'System',
    fontSize: 23,
    fontWeight: '800',
    color: '#1B1630',
    textAlign: 'center',
    marginTop: 30,
    marginBottom: 10,
    lineHeight: 28,
  },
  description: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    color: '#6B6676',
    textAlign: 'center',
    lineHeight: 22,
  },
  footer: {
    height: 100,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 26,
    paddingBottom: 20,
  },
  dotsContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 7,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#DAD3EB',
  },
  activeDot: {
    width: 24,
    backgroundColor: '#5B18E6',
  },
  arrowButton: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#5B18E6',
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#5B18E6',
    shadowOffset: { width: 0, height: 12 },
    shadowOpacity: 0.55,
    shadowRadius: 24,
    elevation: 8,
  },
});
