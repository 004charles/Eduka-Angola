import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { exercicios } from '@/services/api';

interface Exercicio {
  id: number;
  titulo: string;
  tipo: string;
  prazo?: string;
  questoes_count?: number;
  duracao_minutos?: number;
  estado: string;
  nota?: number;
  nota_maxima?: number;
  feedback?: string;
}

function formatDate(dateStr?: string): string {
  if (!dateStr) return '';
  try {
    const d = new Date(dateStr);
    const now = new Date();
    const diffMs = d.getTime() - now.getTime();
    const diffDays = Math.ceil(diffMs / (1000 * 60 * 60 * 24));
    if (diffDays < 0) return 'Prazo expirado';
    if (diffDays === 0) return 'Prazo hoje';
    if (diffDays === 1) return 'Prazo amanhã';
    return `Prazo em ${diffDays} dias`;
  } catch {
    return dateStr;
  }
}

export default function ProvasScreen() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState('Pendentes');
  const [exercises, setExercises] = useState<Exercicio[]>([]);
  const [loading, setLoading] = useState(true);

  const tabs = ['Pendentes', 'Entregues', 'Corrigidas'];

  const fetchExercises = useCallback(async () => {
    try {
      const data = await exercicios.list();
      const list = Array.isArray(data) ? data : data?.results ?? [];
      setExercises(list);
    } catch (e) {
      console.error('Failed to fetch exercises', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchExercises();
  }, [fetchExercises]);

  const pendentes = exercises.filter((e) => e.estado === 'pendente');
  const entregues = exercises.filter((e) => e.estado === 'entregue');
  const corrigidas = exercises.filter((e) => e.estado === 'corrigido');

  const getAccent = (ex: Exercicio) => {
    if (ex.estado === 'corrigido') return { accent: '#159B5E', bg: '#DDF3E8' };
    if (ex.tipo === 'quiz') return { accent: '#5B18E6', bg: '#EDE7FE' };
    return { accent: '#B57A12', bg: '#FBF0D9' };
  };

  const renderCard = (item: Exercicio, showFeedback = false) => {
    const { accent, bg } = getAccent(item);
    const iconName = item.estado === 'corrigido'
      ? 'check-circle-outline'
      : item.tipo === 'quiz'
        ? 'help-circle-outline'
        : 'file-document-outline';
    const deadlineLabel = item.estado === 'corrigido'
      ? `Corrigida${item.nota != null ? ` · ${item.nota}/${item.nota_maxima ?? 20}` : ''}`
      : formatDate(item.prazo);
    const detailsLabel = item.estado === 'corrigido'
      ? item.feedback ?? 'Ver feedback do professor'
      : `${item.questoes_count ?? 0} questões${item.duracao_minutos ? ` · ${item.duracao_minutos} min` : ''}`;
    const btnLabel = item.estado === 'corrigido' ? '' : item.tipo === 'quiz' ? 'Iniciar' : 'Abrir';

    return (
      <View key={item.id} style={styles.card}>
        <View style={styles.cardTop}>
          <View style={[styles.typeIconWrap, { backgroundColor: bg }]}>
            <MaterialCommunityIcons name={iconName} size={22} color={accent} />
          </View>
          <View style={styles.cardInfo}>
            <Text style={styles.cardTitle}>{item.titulo}</Text>
            <Text style={styles.cardDeadline}>{deadlineLabel}</Text>
          </View>
        </View>
        <View style={styles.cardBottom}>
          {showFeedback ? (
            <TouchableOpacity style={styles.feedbackLink}>
              <MaterialCommunityIcons name="message-text-outline" size={14} color="#5B18E6" />
              <Text style={styles.feedbackText}>{detailsLabel}</Text>
            </TouchableOpacity>
          ) : (
            <Text style={styles.cardDetails}>{detailsLabel}</Text>
          )}
          {btnLabel ? (
            <TouchableOpacity
              style={[styles.actionBtn, { backgroundColor: accent }]}
              onPress={() => router.push(`/prova/${item.id}`)}
            >
              <Text style={styles.actionBtnText}>{btnLabel}</Text>
            </TouchableOpacity>
          ) : null}
        </View>
      </View>
    );
  };

  const filtered = activeTab === 'Pendentes' ? pendentes : activeTab === 'Entregues' ? entregues : corrigidas;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />

      {/* Title */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Provas & Tarefas</Text>
      </View>

      {/* Tab switcher */}
      <View style={styles.tabRow}>
        {tabs.map((t) => {
          const isActive = activeTab === t;
          return (
            <TouchableOpacity
              key={t}
              style={[styles.tabPill, isActive && styles.tabPillActive]}
              onPress={() => setActiveTab(t)}
            >
              <Text style={[styles.tabText, isActive && styles.tabTextActive]}>{t}</Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Cards */}
      <ScrollView contentContainerStyle={styles.listContainer} showsVerticalScrollIndicator={false}>
        {loading ? (
          <ActivityIndicator size="large" color="#5B18E6" style={{ marginTop: 60 }} />
        ) : (
          <>
            {activeTab !== 'Entregues' && filtered.length === 0 && (
              <View style={styles.emptyState}>
                <MaterialCommunityIcons
                  name={activeTab === 'Pendentes' ? 'tray-arrow-down' : 'check-circle-outline'}
                  size={48}
                  color="#9A93AD"
                />
                <Text style={styles.emptyText}>
                  {activeTab === 'Pendentes' ? 'Nenhuma prova pendente' : 'Nenhuma prova corrigida'}
                </Text>
              </View>
            )}

            {activeTab === 'Pendentes' && pendentes.map((item) => renderCard(item))}
            {activeTab === 'Corrigidas' && corrigidas.map((item) => renderCard(item, true))}

            {activeTab === 'Entregues' && (
              entregues.length === 0 ? (
                <View style={styles.emptyState}>
                  <MaterialCommunityIcons name="tray-arrow-up" size={48} color="#9A93AD" />
                  <Text style={styles.emptyText}>Nenhuma tarefa entregue</Text>
                </View>
              ) : (
                entregues.map((item) => renderCard(item))
              )
            )}
          </>
        )}
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
  tabRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    gap: 9,
    marginBottom: 16,
  },
  tabPill: {
    paddingHorizontal: 16,
    paddingVertical: 9,
    borderRadius: 99,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    height: 38,
    justifyContent: 'center',
  },
  tabPillActive: {
    backgroundColor: '#5B18E6',
    borderColor: '#5B18E6',
  },
  tabText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5A5567',
  },
  tabTextActive: {
    color: '#ffffff',
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingBottom: 30,
    gap: 14,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    padding: 16,
    gap: 14,
  },
  cardTop: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  typeIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 13,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardInfo: {
    flex: 1,
  },
  cardTitle: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '800',
    color: '#1B1630',
  },
  cardDeadline: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '600',
    color: '#8B8598',
    marginTop: 2,
  },
  cardBottom: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  cardDetails: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '600',
    color: '#8B8598',
  },
  actionBtn: {
    paddingHorizontal: 18,
    paddingVertical: 9,
    borderRadius: 12,
  },
  actionBtnText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '800',
    color: '#ffffff',
  },
  feedbackLink: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
  },
  feedbackText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5B18E6',
  },
  emptyState: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 60,
    gap: 12,
  },
  emptyText: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '600',
    color: '#9A93AD',
  },
});
