import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, StyleSheet, SafeAreaView, ScrollView, TouchableOpacity, StatusBar, ActivityIndicator } from 'react-native';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { aulas } from '@/services/api';

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

const TABS = ['Conteúdo', 'Materiais', 'Notas'];

interface LessonData {
  id: number;
  titulo: string;
  modulo?: { id: number; nome: string; ordem?: number };
  ordem?: number;
  duracao_segundos?: number;
  url_video?: string;
  concluida?: boolean;
  tempo_assistido?: number;
  aulas_modulo?: { id: number; titulo: string; ordem?: number; duracao_segundos?: number; concluida?: boolean }[];
}

function formatTime(seconds?: number): string {
  if (!seconds) return '00:00';
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

export default function AulaDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState('Conteúdo');
  const [lesson, setLesson] = useState<LessonData | null>(null);
  const [loading, setLoading] = useState(true);
  const [marking, setMarking] = useState(false);

  const fetchLesson = useCallback(async () => {
    if (!id) return;
    try {
      const data = await aulas.get(Number(id));
      setLesson(data);
    } catch (e) {
      console.error('Failed to fetch lesson', e);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchLesson();
  }, [fetchLesson]);

  const handleMarkComplete = useCallback(async () => {
    if (!id || marking) return;
    setMarking(true);
    try {
      await aulas.updateProgresso(Number(id), { concluida: true });
      setLesson((prev) => (prev ? { ...prev, concluida: true } : prev));
    } catch (e) {
      console.error('Failed to mark as complete', e);
    } finally {
      setMarking(false);
    }
  }, [id, marking]);

  const sisterLessons = lesson?.aulas_modulo ?? [];
  const currentId = Number(id);
  const progressPercent = lesson?.duracao_segundos
    ? Math.min(100, Math.round(((lesson.tempo_assistido ?? 0) / lesson.duracao_segundos) * 100))
    : 0;

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar barStyle="light-content" backgroundColor="#000" />
        <View style={[styles.videoArea, { justifyContent: 'center', alignItems: 'center' }]}>
          <ActivityIndicator size="large" color="#fff" />
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#000" />

      {/* Video Player Area */}
      <View style={styles.videoArea}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <MaterialCommunityIcons name="arrow-left" size={24} color="#fff" />
        </TouchableOpacity>

        <TouchableOpacity style={styles.playButton} activeOpacity={0.8}>
          <MaterialCommunityIcons name="play" size={40} color="#fff" />
        </TouchableOpacity>

        <View style={styles.progressContainer}>
          <View style={styles.progressTrack}>
            <View style={[styles.progressFill, { width: `${progressPercent}%` }]} />
          </View>
          <View style={styles.timeRow}>
            <Text style={styles.timeText}>{formatTime(lesson?.tempo_assistido)}</Text>
            <Text style={styles.timeText}>{formatTime(lesson?.duracao_segundos)}</Text>
          </View>
        </View>
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Module/Lesson Label */}
        <Text style={styles.moduleLabel}>
          {lesson?.modulo ? `MÓDULO ${lesson.modulo.ordem ?? lesson.modulo.nome}` : 'MÓDULO'}
          {lesson?.ordem ? ` · AULA ${lesson.ordem}` : ''}
        </Text>

        {/* Title */}
        <Text style={styles.title}>{lesson?.titulo ?? 'Aula'}</Text>

        {/* Tab Switcher */}
        <View style={styles.tabRow}>
          {TABS.map((tab) => (
            <TouchableOpacity
              key={tab}
              style={[styles.tab, activeTab === tab && styles.tabActive]}
              onPress={() => setActiveTab(tab)}
            >
              <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
                {tab}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Lesson Items */}
        <View style={styles.lessonList}>
          {sisterLessons.length > 0
            ? sisterLessons.map((les) => {
                const isCurrent = les.id === currentId;
                const isCompleted = les.concluida;
                const iconName = isCompleted
                  ? 'check-circle'
                  : isCurrent
                    ? 'play-circle'
                    : 'lock';
                const iconColor = isCompleted
                  ? COLORS.green
                  : isCurrent
                    ? COLORS.purple
                    : COLORS.gray;

                return (
                  <TouchableOpacity
                    key={les.id}
                    style={[
                      styles.lessonItem,
                      isCurrent && styles.lessonItemPlaying,
                    ]}
                    activeOpacity={0.7}
                    onPress={() => {
                      if (!isCurrent) router.push(`/aula/${les.id}`);
                    }}
                  >
                    <MaterialCommunityIcons name={iconName} size={24} color={iconColor} />
                    <View style={styles.lessonInfo}>
                      <Text
                        style={[
                          styles.lessonTitle,
                          isCurrent && styles.lessonTitlePlaying,
                        ]}
                      >
                        {les.titulo}
                      </Text>
                      {isCurrent && (
                        <Text style={styles.playingNow}>A dar agora</Text>
                      )}
                    </View>
                    <Text style={styles.lessonTime}>{formatTime(les.duracao_segundos)}</Text>
                  </TouchableOpacity>
                );
              })
            : null}
        </View>
      </ScrollView>

      {/* Bottom Bar */}
      <View style={styles.bottomBar}>
        <TouchableOpacity style={styles.skipBtn}>
          <MaterialCommunityIcons name="skip-next" size={20} color={COLORS.gray} />
          <Text style={styles.skipText}>Saltar</Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[styles.completeBtn, lesson?.concluida && { opacity: 0.6 }]}
          activeOpacity={0.8}
          onPress={handleMarkComplete}
          disabled={marking || lesson?.concluida}
        >
          <MaterialCommunityIcons name="check-circle-outline" size={20} color="#fff" />
          <Text style={styles.completeBtnText}>
            {lesson?.concluida ? 'Concluída' : marking ? 'A marcar...' : 'Marcar como concluída'}
          </Text>
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
  videoArea: {
    backgroundColor: '#000',
    aspectRatio: 16 / 9,
    justifyContent: 'center',
    alignItems: 'center',
  },
  backBtn: {
    position: 'absolute',
    top: 12,
    left: 12,
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: 'rgba(0,0,0,0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  playButton: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: 'rgba(91,24,230,0.85)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  progressContainer: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    paddingHorizontal: 12,
    paddingBottom: 10,
  },
  progressTrack: {
    height: 4,
    backgroundColor: 'rgba(255,255,255,0.25)',
    borderRadius: 2,
    marginBottom: 6,
  },
  progressFill: {
    height: '100%',
    backgroundColor: COLORS.purple,
    borderRadius: 2,
  },
  timeRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  timeText: {
    fontSize: 11,
    color: 'rgba(255,255,255,0.7)',
    fontFamily: 'System',
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  moduleLabel: {
    fontSize: 12,
    fontWeight: '700',
    color: COLORS.gray,
    fontFamily: 'System',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginTop: 16,
  },
  title: {
    fontSize: 20,
    fontWeight: '800',
    color: COLORS.dark,
    fontFamily: 'System',
    marginTop: 6,
    marginBottom: 16,
  },
  tabRow: {
    flexDirection: 'row',
    gap: 0,
    marginBottom: 20,
    backgroundColor: '#fff',
    borderRadius: 12,
    padding: 4,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  tab: {
    flex: 1,
    paddingVertical: 10,
    alignItems: 'center',
    borderRadius: 10,
  },
  tabActive: {
    backgroundColor: COLORS.purple,
  },
  tabText: {
    fontSize: 13,
    fontWeight: '600',
    color: COLORS.gray,
    fontFamily: 'System',
  },
  tabTextActive: {
    color: '#fff',
  },
  lessonList: {
    gap: 10,
    marginBottom: 20,
  },
  lessonItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#fff',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
    gap: 12,
  },
  lessonItemPlaying: {
    borderColor: COLORS.purple,
    backgroundColor: COLORS.lightPurple,
  },
  lessonInfo: {
    flex: 1,
  },
  lessonTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.dark,
    fontFamily: 'System',
  },
  lessonTitlePlaying: {
    color: COLORS.purple,
  },
  playingNow: {
    fontSize: 11,
    fontWeight: '600',
    color: COLORS.purple,
    fontFamily: 'System',
    marginTop: 2,
  },
  lessonTime: {
    fontSize: 12,
    fontWeight: '500',
    color: COLORS.gray,
    fontFamily: 'System',
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
  skipBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: COLORS.border,
  },
  skipText: {
    fontSize: 14,
    fontWeight: '600',
    color: COLORS.gray,
    fontFamily: 'System',
  },
  completeBtn: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    backgroundColor: COLORS.purple,
    borderRadius: 12,
    paddingVertical: 14,
  },
  completeBtnText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#fff',
    fontFamily: 'System',
  },
});
