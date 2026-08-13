import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { aluno } from '@/services/api';

interface Inscricao {
  id: number;
  curso: {
    id: number;
    titulo: string;
    modulos_count?: number;
  };
  progresso_percentual: number;
  aulas_concluidas: number;
  total_aulas: number;
  horas_assistidas?: number;
  estado: string;
}

export default function AprendizagemScreen() {
  const router = useRouter();
  const [inscricoes, setInscricoes] = useState<Inscricao[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchInscricoes = useCallback(async () => {
    try {
      const data = await aluno.getInscricoes();
      const list = Array.isArray(data) ? data : data?.results ?? [];
      setInscricoes(list);
    } catch (e) {
      console.error('Failed to fetch inscricoes', e);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchInscricoes();
  }, [fetchInscricoes]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchInscricoes();
  }, [fetchInscricoes]);

  const emAndamento = inscricoes.filter((i) => i.estado !== 'concluida' && i.progresso_percentual > 0);
  const concluidos = inscricoes.filter((i) => i.estado === 'concluida');
  const ativos = inscricoes.filter((i) => i.estado !== 'concluida');

  const totalHoras = inscricoes.reduce((acc, i) => acc + (i.horas_assistidas ?? 0), 0);
  const overallProgress = inscricoes.length
    ? Math.round(inscricoes.reduce((acc, i) => acc + i.progresso_percentual, 0) / inscricoes.length)
    : 0;

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />

      <ScrollView
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#5B18E6" />}
      >
        {/* Title */}
        <View style={styles.header}>
          <Text style={styles.headerTitle}>Meus cursos</Text>
        </View>

        {loading ? (
          <ActivityIndicator size="large" color="#5B18E6" style={{ marginTop: 60 }} />
        ) : (
          <>
            {/* Purple summary card */}
            <View style={styles.summaryCard}>
              <View style={styles.progressCircle}>
                <Text style={styles.progressPercent}>{overallProgress}%</Text>
                <Text style={styles.progressLabel}>Progresso</Text>
              </View>
              <View style={styles.statsCol}>
                <View style={styles.statRow}>
                  <View style={[styles.statIconWrap, { backgroundColor: 'rgba(255,255,255,0.18)' }]}>
                    <MaterialCommunityIcons name="book-open-variant" size={18} color="#ffffff" />
                  </View>
                  <Text style={styles.statValue}>{ativos.length}</Text>
                  <Text style={styles.statLabel}>Cursos ativos</Text>
                </View>
                <View style={styles.statRow}>
                  <View style={[styles.statIconWrap, { backgroundColor: 'rgba(255,255,255,0.18)' }]}>
                    <MaterialCommunityIcons name="check-circle-outline" size={18} color="#ffffff" />
                  </View>
                  <Text style={styles.statValue}>{concluidos.length}</Text>
                  <Text style={styles.statLabel}>Concluídos</Text>
                </View>
                <View style={styles.statRow}>
                  <View style={[styles.statIconWrap, { backgroundColor: 'rgba(255,255,255,0.18)' }]}>
                    <MaterialCommunityIcons name="clock-outline" size={18} color="#ffffff" />
                  </View>
                  <Text style={styles.statValue}>{totalHoras}h</Text>
                  <Text style={styles.statLabel}>Horas</Text>
                </View>
              </View>
            </View>

            {/* Em andamento */}
            <View style={styles.sectionRow}>
              <Text style={styles.sectionTitle}>Em andamento</Text>
            </View>

            {emAndamento.length === 0 && (
              <Text style={{ textAlign: 'center', color: '#8B8598', marginTop: 20 }}>Nenhum curso em andamento</Text>
            )}

            {emAndamento.map((item) => (
              <TouchableOpacity
                key={item.id}
                style={styles.courseCard}
                activeOpacity={0.7}
                onPress={() => router.push(`/curso/${item.curso.id}`)}
              >
                <View style={styles.cardLeft}>
                  <View style={styles.playIconWrap}>
                    <MaterialCommunityIcons name="play" size={20} color="#ffffff" />
                  </View>
                </View>
                <View style={styles.cardBody}>
                  <Text style={styles.cardTitle} numberOfLines={1}>{item.curso.titulo}</Text>
                  <Text style={styles.cardSub}>
                    {item.aulas_concluidas} de {item.total_aulas} aulas
                  </Text>
                  <View style={styles.progressBg}>
                    <View style={[styles.progressFill, { width: `${item.progresso_percentual}%` }]} />
                  </View>
                  <Text style={styles.progressText}>{item.progresso_percentual}%</Text>
                </View>
              </TouchableOpacity>
            ))}
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
  scrollContent: {
    paddingBottom: 30,
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
  summaryCard: {
    flexDirection: 'row',
    marginHorizontal: 20,
    backgroundColor: '#4711C4',
    borderRadius: 22,
    padding: 20,
    gap: 24,
    shadowColor: '#4711C4',
    shadowOffset: { width: 0, height: 16 },
    shadowOpacity: 0.5,
    shadowRadius: 30,
    elevation: 8,
  },
  progressCircle: {
    width: 90,
    height: 90,
    borderRadius: 45,
    borderWidth: 6,
    borderColor: 'rgba(255,255,255,0.3)',
    backgroundColor: 'rgba(255,255,255,0.08)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressPercent: {
    fontFamily: 'System',
    fontSize: 20,
    fontWeight: '800',
    color: '#ffffff',
  },
  progressLabel: {
    fontFamily: 'System',
    fontSize: 9,
    fontWeight: '600',
    color: 'rgba(255,255,255,0.8)',
    marginTop: 1,
  },
  statsCol: {
    flex: 1,
    justifyContent: 'center',
    gap: 8,
  },
  statRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  statIconWrap: {
    width: 28,
    height: 28,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  statValue: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '800',
    color: '#ffffff',
    minWidth: 30,
  },
  statLabel: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: 'rgba(255,255,255,0.75)',
  },
  sectionRow: {
    paddingHorizontal: 20,
    marginTop: 24,
    marginBottom: 12,
  },
  sectionTitle: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '800',
    color: '#1B1630',
  },
  courseCard: {
    flexDirection: 'row',
    marginHorizontal: 20,
    marginBottom: 12,
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    padding: 14,
    gap: 14,
  },
  cardLeft: {
    justifyContent: 'center',
  },
  playIconWrap: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#5B18E6',
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardBody: {
    flex: 1,
  },
  cardTitle: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '800',
    color: '#1B1630',
    marginBottom: 3,
  },
  cardSub: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: '#8B8598',
    marginBottom: 10,
  },
  progressBg: {
    height: 7,
    backgroundColor: '#ECE8F3',
    borderRadius: 99,
    marginBottom: 5,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#5B18E6',
    borderRadius: 99,
  },
  progressText: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '700',
    color: '#5B18E6',
    textAlign: 'right',
  },
});
