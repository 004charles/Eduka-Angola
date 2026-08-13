import React, { useState } from 'react';
import { View, Text, StyleSheet, SafeAreaView, TouchableOpacity, StatusBar } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';

const COLORS = {
  purple: '#5B18E6',
  dark: '#1B1630',
  gray: '#8B8598',
  bg: '#F6F5FA',
  border: '#ECE8F3',
  lightPurple: '#EDE7FE',
  green: '#159B5E',
  red: '#E8433D',
};

const OPTIONS = [
  { letter: 'A', text: 'display: block' },
  { letter: 'B', text: 'display: flex' },
  { letter: 'C', text: 'position: absolute' },
  { letter: 'D', text: 'float: left' },
];

export default function ProvaDetailScreen() {
  const router = useRouter();
  const [selected, setSelected] = useState('B');
  const progress = 30;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" backgroundColor={COLORS.bg} />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={() => router.back()} style={styles.closeBtn}>
          <MaterialCommunityIcons name="close" size={24} color={COLORS.dark} />
        </TouchableOpacity>
        <Text style={styles.questionCount}>Questão 3 de 10</Text>
        <View style={styles.timerBadge}>
          <MaterialCommunityIcons name="clock-outline" size={16} color={COLORS.red} />
          <Text style={styles.timerText}>18:42</Text>
        </View>
      </View>

      {/* Progress Bar */}
      <View style={styles.progressContainer}>
        <View style={styles.progressTrack}>
          <View style={[styles.progressFill, { width: `${progress}%` }]} />
        </View>
      </View>

      <View style={styles.content}>
        {/* Label */}
        <Text style={styles.label}>MÚLTIPLA ESCOLHA</Text>

        {/* Question */}
        <Text style={styles.question}>
          Qual propriedade CSS é usada para criar um layout flexível em uma dimensão?
        </Text>

        {/* Options */}
        <View style={styles.optionsList}>
          {OPTIONS.map((option) => {
            const isSelected = selected === option.letter;
            return (
              <TouchableOpacity
                key={option.letter}
                style={[styles.option, isSelected && styles.optionSelected]}
                onPress={() => setSelected(option.letter)}
                activeOpacity={0.7}
              >
                <View style={[styles.radio, isSelected && styles.radioSelected]}>
                  {isSelected && <View style={styles.radioDot} />}
                </View>
                <Text style={[styles.optionLetter, isSelected && styles.optionLetterSelected]}>
                  {option.letter}
                </Text>
                <Text style={[styles.optionText, isSelected && styles.optionTextSelected]}>
                  {option.text}
                </Text>
              </TouchableOpacity>
            );
          })}
        </View>
      </View>

      {/* Bottom Buttons */}
      <View style={styles.bottomBar}>
        <TouchableOpacity style={styles.prevBtn}>
          <MaterialCommunityIcons name="chevron-left" size={20} color={COLORS.gray} />
          <Text style={styles.prevText}>Anterior</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.nextBtn} activeOpacity={0.8}>
          <Text style={styles.nextText}>Próxima</Text>
          <MaterialCommunityIcons name="chevron-right" size={20} color="#fff" />
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: COLORS.bg,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
  },
  closeBtn: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  questionCount: {
    fontSize: 15,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  timerBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: '#FEE2E2',
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 20,
  },
  timerText: {
    fontSize: 14,
    fontWeight: '700',
    color: COLORS.red,
    fontFamily: 'System',
  },
  progressContainer: {
    paddingHorizontal: 20,
    marginBottom: 24,
  },
  progressTrack: {
    height: 6,
    backgroundColor: COLORS.border,
    borderRadius: 3,
  },
  progressFill: {
    height: '100%',
    backgroundColor: COLORS.purple,
    borderRadius: 3,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  label: {
    fontSize: 11,
    fontWeight: '700',
    color: COLORS.purple,
    fontFamily: 'System',
    textTransform: 'uppercase',
    letterSpacing: 1,
    marginBottom: 10,
  },
  question: {
    fontSize: 18,
    fontWeight: '700',
    color: COLORS.dark,
    fontFamily: 'System',
    lineHeight: 26,
    marginBottom: 28,
  },
  optionsList: {
    gap: 12,
  },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 16,
    borderWidth: 1.5,
    borderColor: COLORS.border,
    gap: 12,
  },
  optionSelected: {
    borderColor: COLORS.purple,
    backgroundColor: COLORS.lightPurple,
  },
  radio: {
    width: 22,
    height: 22,
    borderRadius: 11,
    borderWidth: 2,
    borderColor: COLORS.border,
    justifyContent: 'center',
    alignItems: 'center',
  },
  radioSelected: {
    borderColor: COLORS.purple,
  },
  radioDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
    backgroundColor: COLORS.purple,
  },
  optionLetter: {
    fontSize: 15,
    fontWeight: '700',
    color: COLORS.gray,
    fontFamily: 'System',
    width: 20,
  },
  optionLetterSelected: {
    color: COLORS.purple,
  },
  optionText: {
    fontSize: 15,
    fontWeight: '500',
    color: COLORS.dark,
    fontFamily: 'System',
    flex: 1,
  },
  optionTextSelected: {
    color: COLORS.purple,
    fontWeight: '600',
  },
  bottomBar: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 14,
    backgroundColor: '#fff',
    borderTopWidth: 1,
    borderTopColor: COLORS.border,
    gap: 12,
  },
  prevBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  prevText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.gray,
    fontFamily: 'System',
  },
  nextBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    backgroundColor: COLORS.purple,
    borderRadius: 12,
    paddingVertical: 14,
  },
  nextText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#fff',
    fontFamily: 'System',
  },
});
