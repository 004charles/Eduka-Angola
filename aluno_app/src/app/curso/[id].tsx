import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter, useLocalSearchParams } from 'expo-router';
import { cursos } from '@/services/api';

export default function CourseDetailScreen() {
  const router = useRouter();
  const { id } = useLocalSearchParams<{ id: string }>();
  const [activeTab, setActiveTab] = useState('Sobre');
  const [course, setCourse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);
  const [favoriting, setFavoriting] = useState(false);

  const fetchCourse = useCallback(async () => {
    try {
      const data = await cursos.get(Number(id));
      setCourse(data);
    } catch (err: any) {
      Alert.alert('Erro', err.message || 'Não foi possível carregar o curso.');
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchCourse();
  }, [fetchCourse]);

  const handleEnroll = useCallback(async () => {
    setEnrolling(true);
    try {
      await cursos.inscrever(Number(id));
      Alert.alert('Sucesso', 'Inscrição realizada com sucesso!');
    } catch (err: any) {
      Alert.alert('Erro', err.message || 'Não foi possível inscrever-se.');
    } finally {
      setEnrolling(false);
    }
  }, [id]);

  const handleFavorite = useCallback(async () => {
    setFavoriting(true);
    try {
      await cursos.favoritar(Number(id));
      Alert.alert('Sucesso', 'Ação de favorito registada!');
    } catch (err: any) {
      Alert.alert('Erro', err.message || 'Não foi possível favoritar.');
    } finally {
      setFavoriting(false);
    }
  }, [id]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <StatusBar style="light" />
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <ActivityIndicator size="large" color="#5B18E6" />
        </View>
      </SafeAreaView>
    );
  }

  const courseTitle = course?.titulo ?? 'Curso';
  const courseCategory = course?.categoria_nome ?? 'Categoria';
  const courseInstitution = course?.centro_nome ?? '';
  const courseDescription = course?.descricao ?? '';
  const coursePrice = course?.preco != null ? `${Number(course.preco).toLocaleString('pt-AO')} Kz` : 'Gratuito';
  const courseRating = course?.rating ?? '4,8';
  const courseAvaliacaoCount = course?.avaliacao_count ?? 312;
  const courseDuracao = course?.duracao ?? '12 sem.';
  const courseAulas = course?.total_aulas ?? 48;
  const temCertificado = course?.tem_certificado ?? true;
  const objetivos = course?.objetivos ?? [
    'Estrutura semântica com HTML5',
    'Estilização avançada com CSS3',
    'Programação dinâmica com JavaScript',
    'Consumo de APIs RESTful',
    'Deploy e publicação de sites',
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />

      {/* Purple striped header */}
      <View style={styles.header}>
        <View style={styles.headerStripes} />
        <View style={styles.headerContent}>
          <TouchableOpacity style={styles.headerBtn} onPress={() => router.back()}>
            <MaterialCommunityIcons name="arrow-left" size={22} color="#ffffff" />
          </TouchableOpacity>
          <View style={styles.headerActions}>
            <TouchableOpacity style={styles.headerBtn} onPress={handleFavorite} disabled={favoriting}>
              <MaterialCommunityIcons name="heart-outline" size={22} color="#ffffff" />
            </TouchableOpacity>
            <TouchableOpacity style={styles.headerBtn}>
              <MaterialCommunityIcons name="share-variant-outline" size={22} color="#ffffff" />
            </TouchableOpacity>
          </View>
        </View>
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent} showsVerticalScrollIndicator={false}>
        {/* Category badge and rating */}
        <View style={styles.metaRow}>
          <View style={styles.categoryBadge}>
            <Text style={styles.categoryText}>{courseCategory}</Text>
          </View>
          <View style={styles.ratingRow}>
            <MaterialCommunityIcons name="star" size={14} color="#E8A63D" />
            <Text style={styles.ratingText}>{courseRating} ({courseAvaliacaoCount})</Text>
          </View>
        </View>

        {/* Title */}
        <Text style={styles.title}>{courseTitle}</Text>

        {/* Institution */}
        <TouchableOpacity style={styles.institutionRow}>
          <Text style={styles.institutionName}>{courseInstitution}</Text>
          <MaterialCommunityIcons name="check-decagram" size={16} color="#5B18E6" />
        </TouchableOpacity>

        {/* Stats row */}
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <MaterialCommunityIcons name="calendar-clock-outline" size={18} color="#5B18E6" />
            <Text style={styles.statText}>{courseDuracao}</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <MaterialCommunityIcons name="play-circle-outline" size={18} color="#5B18E6" />
            <Text style={styles.statText}>{courseAulas} aulas</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <MaterialCommunityIcons name="certificate-outline" size={18} color="#5B18E6" />
            <Text style={styles.statText}>{temCertificado ? 'Certificado' : 'Sem certificado'}</Text>
          </View>
        </View>

        {/* Tab switcher */}
        <View style={styles.tabRow}>
          {['Sobre', 'Conteúdo', 'Avaliações'].map((tab) => (
            <TouchableOpacity
              key={tab}
              style={[styles.tabItem, activeTab === tab && styles.tabItemActive]}
              onPress={() => setActiveTab(tab)}
            >
              <Text style={[styles.tabText, activeTab === tab && styles.tabTextActive]}>
                {tab}
              </Text>
              {activeTab === tab && <View style={styles.tabIndicator} />}
            </TouchableOpacity>
          ))}
        </View>

        {/* Description */}
        <View style={styles.section}>
          <Text style={styles.description}>
            {courseDescription || 'Este curso introdutório abrange os fundamentos do desenvolvimento web moderno.'}
          </Text>
        </View>

        {/* O que vai aprender */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>O que vai aprender</Text>
          <View style={styles.checkList}>
            {Array.isArray(objetivos) && objetivos.map((item: string, index: number) => (
              <View key={index} style={styles.checkItem}>
                <View style={styles.checkIcon}>
                  <MaterialCommunityIcons name="check" size={14} color="#5B18E6" />
                </View>
                <Text style={styles.checkText}>{item}</Text>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>

      {/* Bottom bar */}
      <View style={styles.bottomBar}>
        <View style={styles.priceContainer}>
          <Text style={styles.priceLabel}>Preço</Text>
          <Text style={styles.priceValue}>{coursePrice}</Text>
        </View>
        <TouchableOpacity
          style={styles.enrollButton}
          onPress={handleEnroll}
          disabled={enrolling}
        >
          {enrolling ? (
            <ActivityIndicator size="small" color="#ffffff" />
          ) : (
            <Text style={styles.enrollText}>Inscrever-se</Text>
          )}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F6F5FA',
  },
  header: {
    backgroundColor: '#5B18E6',
    paddingTop: 10,
    paddingBottom: 20,
    paddingHorizontal: 20,
    overflow: 'hidden',
  },
  headerStripes: {
    ...StyleSheet.absoluteFillObject,
    opacity: 0.12,
    backgroundColor: 'transparent',
    borderTopWidth: 40,
    borderTopColor: 'rgba(255,255,255,0.08)',
    borderRightWidth: 40,
    borderRightColor: 'transparent',
  },
  headerContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  headerBtn: {
    width: 40,
    height: 40,
    borderRadius: 12,
    backgroundColor: 'rgba(255, 255, 255, 0.18)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerActions: {
    flexDirection: 'row',
    gap: 10,
  },
  metaRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    marginTop: 18,
  },
  categoryBadge: {
    backgroundColor: '#EDE7FE',
    paddingHorizontal: 10,
    paddingVertical: 5,
    borderRadius: 8,
  },
  categoryText: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '700',
    color: '#5B18E6',
  },
  ratingRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  ratingText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '600',
    color: '#1B1630',
  },
  title: {
    fontFamily: 'System',
    fontSize: 20,
    fontWeight: '800',
    color: '#1B1630',
    paddingHorizontal: 20,
    marginTop: 12,
    lineHeight: 26,
  },
  institutionRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 20,
    marginTop: 10,
  },
  institutionName: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '600',
    color: '#8B8598',
  },
  statsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#ffffff',
    marginHorizontal: 20,
    marginTop: 18,
    paddingVertical: 14,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    gap: 0,
  },
  statItem: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
  },
  statText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '600',
    color: '#1B1630',
  },
  statDivider: {
    width: 1,
    height: 20,
    backgroundColor: '#ECE8F3',
  },
  tabRow: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    marginTop: 22,
    borderBottomWidth: 1,
    borderBottomColor: '#ECE8F3',
  },
  tabItem: {
    paddingVertical: 12,
    marginRight: 24,
    position: 'relative',
  },
  tabItemActive: {},
  tabText: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '600',
    color: '#8B8598',
  },
  tabTextActive: {
    fontWeight: '800',
    color: '#5B18E6',
  },
  tabIndicator: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: 3,
    backgroundColor: '#5B18E6',
    borderRadius: 2,
  },
  section: {
    paddingHorizontal: 20,
    marginTop: 20,
  },
  description: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    color: '#4A4557',
    lineHeight: 22,
  },
  sectionTitle: {
    fontFamily: 'System',
    fontSize: 16,
    fontWeight: '800',
    color: '#1B1630',
    marginBottom: 14,
  },
  checkList: {
    gap: 12,
  },
  checkItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
  },
  checkIcon: {
    width: 28,
    height: 28,
    borderRadius: 8,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkText: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '500',
    color: '#1B1630',
    flex: 1,
  },
  bottomBar: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#ffffff',
    paddingHorizontal: 20,
    paddingVertical: 14,
    borderTopWidth: 1,
    borderTopColor: '#ECE8F3',
  },
  priceContainer: {
    gap: 2,
  },
  priceLabel: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#8B8598',
  },
  priceValue: {
    fontFamily: 'System',
    fontSize: 18,
    fontWeight: '800',
    color: '#1B1630',
  },
  enrollButton: {
    backgroundColor: '#5B18E6',
    paddingHorizontal: 28,
    paddingVertical: 14,
    borderRadius: 14,
  },
  enrollText: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '800',
    color: '#ffffff',
  },
});
