import React from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';

const PATHS = [
  {
    id: 1,
    title: 'Desenvolvimento Web Full-Stack',
    courses: 4,
    hours: '~120h',
    progress: 40,
    steps: [
      { label: 'HTML & CSS', status: 'done' },
      { label: 'JavaScript', status: 'active' },
      { label: 'Back-end', status: 'locked' },
    ],
  },
  {
    id: 2,
    title: 'Fundamentos de Enfermagem',
    courses: 5,
    hours: '~200h',
    progress: 0,
    steps: [],
  },
];

export default function TrilhasScreen() {
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Trilhas</Text>
        <Text style={styles.headerSubtitle}>Percursos estruturados para dominar uma área</Text>
      </View>

      <ScrollView contentContainerStyle={styles.listContainer} showsVerticalScrollIndicator={false}>
        {PATHS.map((path) => (
          <View key={path.id} style={styles.pathCard}>
            {/* Card header */}
            <View style={styles.cardHeader}>
              <View style={styles.cardTitleRow}>
                <View style={styles.iconCircle}>
                  <MaterialCommunityIcons name="route" size={22} color="#5B18E6" />
                </View>
                <View style={styles.cardTitleInfo}>
                  <Text style={styles.pathTitle} numberOfLines={2}>{path.title}</Text>
                  <Text style={styles.pathMeta}>{path.courses} cursos · {path.hours}</Text>
                </View>
              </View>
            </View>

            {/* Steps (only for first path) */}
            {path.steps.length > 0 && (
              <View style={styles.stepsContainer}>
                {path.steps.map((step, index) => {
                  const isDone = step.status === 'done';
                  const isActive = step.status === 'active';
                  const isLocked = step.status === 'locked';

                  return (
                    <View key={index} style={styles.stepRow}>
                      {/* Step indicator */}
                      <View style={styles.stepIndicatorCol}>
                        <View
                          style={[
                            styles.stepDot,
                            isDone && styles.stepDotDone,
                            isActive && styles.stepDotActive,
                            isLocked && styles.stepDotLocked,
                          ]}
                        >
                          {isDone && (
                            <MaterialCommunityIcons name="check" size={12} color="#ffffff" />
                          )}
                          {isActive && <View style={styles.stepDotInner} />}
                          {isLocked && (
                            <MaterialCommunityIcons name="lock-outline" size={10} color="#8B8598" />
                          )}
                        </View>
                        {index < path.steps.length - 1 && (
                          <View
                            style={[
                              styles.stepLine,
                              isDone && styles.stepLineDone,
                            ]}
                          />
                        )}
                      </View>

                      {/* Step label */}
                      <View style={styles.stepContent}>
                        <Text
                          style={[
                            styles.stepLabel,
                            isDone && styles.stepLabelDone,
                            isActive && styles.stepLabelActive,
                            isLocked && styles.stepLabelLocked,
                          ]}
                        >
                          {step.label}
                        </Text>
                        {isActive && (
                          <Text style={styles.stepStatus}>Em progresso</Text>
                        )}
                        {isDone && (
                          <Text style={styles.stepStatusDone}>Concluído</Text>
                        )}
                        {isLocked && (
                          <Text style={styles.stepStatusLocked}>Bloqueado</Text>
                        )}
                      </View>
                    </View>
                  );
                })}
              </View>
            )}

            {/* Progress bar (only for first path) */}
            {path.progress > 0 && (
              <View style={styles.progressSection}>
                <View style={styles.progressBarBg}>
                  <View style={[styles.progressBarFill, { width: `${path.progress}%` }]} />
                </View>
                <Text style={styles.progressText}>{path.progress}%</Text>
              </View>
            )}

            {/* Action button */}
            <View style={styles.cardFooter}>
              {path.progress > 0 ? (
                <TouchableOpacity style={styles.continueBtn}>
                  <MaterialCommunityIcons name="play-circle-outline" size={18} color="#ffffff" />
                  <Text style={styles.continueText}>Continuar</Text>
                </TouchableOpacity>
              ) : (
                <TouchableOpacity style={styles.viewBtn}>
                  <Text style={styles.viewText}>Ver</Text>
                  <MaterialCommunityIcons name="arrow-right" size={16} color="#5B18E6" />
                </TouchableOpacity>
              )}
            </View>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F6F5FA',
  },
  header: {
    paddingHorizontal: 20,
    paddingVertical: 14,
  },
  headerTitle: {
    fontFamily: 'System',
    fontSize: 19,
    fontWeight: '800',
    color: '#1B1630',
  },
  headerSubtitle: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '500',
    color: '#8B8598',
    marginTop: 4,
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 20,
    gap: 18,
  },
  pathCard: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    padding: 18,
  },
  cardHeader: {
    marginBottom: 16,
  },
  cardTitleRow: {
    flexDirection: 'row',
    gap: 14,
  },
  iconCircle: {
    width: 48,
    height: 48,
    borderRadius: 14,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardTitleInfo: {
    flex: 1,
  },
  pathTitle: {
    fontFamily: 'System',
    fontSize: 15,
    fontWeight: '800',
    color: '#1B1630',
    lineHeight: 20,
  },
  pathMeta: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: '#8B8598',
    marginTop: 4,
  },
  stepsContainer: {
    marginLeft: 6,
    marginBottom: 16,
  },
  stepRow: {
    flexDirection: 'row',
    gap: 14,
  },
  stepIndicatorCol: {
    alignItems: 'center',
    width: 24,
  },
  stepDot: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#ECE8F3',
    backgroundColor: '#ffffff',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepDotDone: {
    backgroundColor: '#159B5E',
    borderColor: '#159B5E',
  },
  stepDotActive: {
    borderColor: '#5B18E6',
    backgroundColor: '#ffffff',
  },
  stepDotLocked: {
    backgroundColor: '#F6F5FA',
    borderColor: '#ECE8F3',
  },
  stepDotInner: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#5B18E6',
  },
  stepLine: {
    width: 2,
    flex: 1,
    backgroundColor: '#ECE8F3',
    marginVertical: 4,
  },
  stepLineDone: {
    backgroundColor: '#159B5E',
  },
  stepContent: {
    paddingBottom: 16,
    flex: 1,
  },
  stepLabel: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '700',
    color: '#1B1630',
  },
  stepLabelDone: {
    color: '#159B5E',
  },
  stepLabelActive: {
    color: '#5B18E6',
  },
  stepLabelLocked: {
    color: '#8B8598',
  },
  stepStatus: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#5B18E6',
    marginTop: 2,
  },
  stepStatusDone: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#159B5E',
    marginTop: 2,
  },
  stepStatusLocked: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#8B8598',
    marginTop: 2,
  },
  progressSection: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    marginBottom: 16,
  },
  progressBarBg: {
    flex: 1,
    height: 8,
    backgroundColor: '#ECE8F3',
    borderRadius: 99,
    overflow: 'hidden',
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: '#5B18E6',
    borderRadius: 99,
  },
  progressText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5B18E6',
    minWidth: 36,
    textAlign: 'right',
  },
  cardFooter: {
    alignItems: 'flex-start',
  },
  continueBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#5B18E6',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
  },
  continueText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '700',
    color: '#ffffff',
  },
  viewBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: '#EDE7FE',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 12,
  },
  viewText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '700',
    color: '#5B18E6',
  },
});
