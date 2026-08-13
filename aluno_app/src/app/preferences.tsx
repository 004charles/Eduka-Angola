import React, { useState } from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { StatusBar } from 'expo-status-bar';

const INTERESTS = [
  { name: 'Tecnologia', defaultSelected: true },
  { name: 'Gestão', defaultSelected: false },
  { name: 'Saúde', defaultSelected: true },
  { name: 'Idiomas', defaultSelected: false },
  { name: 'Direito', defaultSelected: false },
  { name: 'Design', defaultSelected: true },
  { name: 'Engenharia', defaultSelected: false },
];

const STUDY_GOALS = [
  { id: 'light', hours: '3h', label: 'leve' },
  { id: 'regular', hours: '5h', label: 'regular', defaultSelected: true },
  { id: 'intense', hours: '10h', label: 'intenso' },
];

export default function PreferencesScreen() {
  const router = useRouter();
  const [selectedInterests, setSelectedInterests] = useState(
    INTERESTS.filter((i) => i.defaultSelected).map((i) => i.name)
  );
  const [selectedGoal, setSelectedGoal] = useState('regular');

  const toggleInterest = (interest: string) => {
    if (selectedInterests.includes(interest)) {
      setSelectedInterests(selectedInterests.filter((i) => i !== interest));
    } else {
      setSelectedInterests([...selectedInterests, interest]);
    }
  };

  const handleContinue = () => {
    // Navigate to the Tab Dashboard Home Screen
    router.replace('/(tabs)/home');
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Progress Bar Header */}
        <View style={styles.progressContainer}>
          <View style={styles.progressBarBg}>
            <View style={styles.progressBarFill} />
          </View>
        </View>

        {/* Header Text */}
        <Text style={styles.title}>O que quer aprender?</Text>
        <Text style={styles.subtitle}>
          Escolha as áreas de interesse para recomendações inteligentes.
        </Text>

        {/* Interests Chip Grid */}
        <View style={styles.interestsGrid}>
          {INTERESTS.map((item) => {
            const isSelected = selectedInterests.includes(item.name);
            return (
              <TouchableOpacity
                key={item.name}
                style={[
                  styles.chip,
                  isSelected ? styles.chipSelected : styles.chipUnselected,
                ]}
                onPress={() => toggleInterest(item.name)}
              >
                <Text
                  style={[
                    styles.chipText,
                    isSelected ? styles.chipTextSelected : styles.chipTextUnselected,
                  ]}
                >
                  {item.name}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>

        {/* Goal Section Title */}
        <Text style={styles.goalSectionTitle}>Meta semanal de estudo</Text>

        {/* Goal Card Grid */}
        <View style={styles.goalsContainer}>
          {STUDY_GOALS.map((goal) => {
            const isSelected = selectedGoal === goal.id;
            return (
              <TouchableOpacity
                key={goal.id}
                style={[
                  styles.goalCard,
                  isSelected ? styles.goalCardSelected : styles.goalCardUnselected,
                ]}
                onPress={() => setSelectedGoal(goal.id)}
              >
                <Text
                  style={[
                    styles.goalHours,
                    isSelected ? styles.goalHoursSelected : styles.goalHoursUnselected,
                  ]}
                >
                  {goal.hours}
                </Text>
                <Text
                  style={[
                    styles.goalLabel,
                    isSelected ? styles.goalLabelSelected : styles.goalLabelUnselected,
                  ]}
                >
                  {goal.label}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </ScrollView>

      {/* Button Footer */}
      <View style={styles.footer}>
        <TouchableOpacity style={styles.continueButton} onPress={handleContinue}>
          <Text style={styles.continueButtonText}>Continuar</Text>
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
  scrollContent: {
    paddingHorizontal: 22,
    paddingTop: 8,
  },
  progressContainer: {
    height: 6,
    width: '100%',
    marginBottom: 20,
  },
  progressBarBg: {
    height: '100%',
    backgroundColor: '#EDE9F5',
    borderRadius: 99,
  },
  progressBarFill: {
    height: '100%',
    width: '100%',
    backgroundColor: '#5B18E6',
    borderRadius: 99,
  },
  title: {
    fontFamily: 'System',
    fontSize: 21,
    fontWeight: '800',
    color: '#1B1630',
    marginBottom: 6,
  },
  subtitle: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '500',
    color: '#6B6676',
    marginBottom: 18,
    lineHeight: 18,
  },
  interestsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 10,
    marginBottom: 26,
  },
  chip: {
    paddingHorizontal: 16,
    paddingVertical: 11,
    borderRadius: 99,
  },
  chipSelected: {
    backgroundColor: '#5B18E6',
  },
  chipUnselected: {
    backgroundColor: '#F5F3FB',
    borderWidth: 1,
    borderColor: '#E9E5F4',
  },
  chipText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '700',
  },
  chipTextSelected: {
    color: '#ffffff',
  },
  chipTextUnselected: {
    color: '#5A5567',
  },
  goalSectionTitle: {
    fontFamily: 'System',
    fontSize: 15,
    fontWeight: '800',
    color: '#1B1630',
    marginBottom: 12,
  },
  goalsContainer: {
    flexDirection: 'row',
    gap: 10,
  },
  goalCard: {
    flex: 1,
    borderRadius: 15,
    paddingVertical: 16,
    paddingHorizontal: 8,
    alignItems: 'center',
    textAlign: 'center',
    borderWidth: 1.5,
  },
  goalCardSelected: {
    backgroundColor: '#EDE7FE',
    borderColor: '#5B18E6',
  },
  goalCardUnselected: {
    backgroundColor: '#F5F3FB',
    borderColor: '#E9E5F4',
  },
  goalHours: {
    fontFamily: 'System',
    fontSize: 18,
    fontWeight: '800',
  },
  goalHoursSelected: {
    color: '#5B18E6',
  },
  goalHoursUnselected: {
    color: '#4A4557',
  },
  goalLabel: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '600',
    marginTop: 2,
  },
  goalLabelSelected: {
    color: '#5B18E6',
  },
  goalLabelUnselected: {
    color: '#8B8598',
  },
  footer: {
    paddingHorizontal: 22,
    paddingBottom: 30,
    backgroundColor: '#ffffff',
  },
  continueButton: {
    backgroundColor: '#5B18E6',
    borderRadius: 15,
    paddingVertical: 16,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#5B18E6',
    shadowOffset: { width: 0, height: 14 },
    shadowOpacity: 0.5,
    shadowRadius: 26,
    elevation: 6,
  },
  continueButtonText: {
    fontFamily: 'System',
    fontSize: 15,
    fontWeight: '800',
    color: '#ffffff',
  },
});
