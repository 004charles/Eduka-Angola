import React, { useEffect, useState, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { aluno } from '@/services/api';

const COLORS_BG = ['#EDE7FE', '#DDF3E8', '#FBF0D9', '#FDECEC'];
const COLORS_TAG = ['#5B18E6', '#159B5E', '#B57A12', '#E8433D'];

export default function FavoritesScreen() {
  const router = useRouter();
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [favorites, setFavorites] = useState<any[]>([]);

  useEffect(() => {
    loadFavorites();
  }, []);

  async function loadFavorites() {
    try {
      setLoading(true);
      const data = await aluno.getFavoritos();
      setFavorites(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao carregar favoritos:', err);
    } finally {
      setLoading(false);
    }
  }

  const onRefresh = useCallback(async () => {
    try {
      setRefreshing(true);
      const data = await aluno.getFavoritos();
      setFavorites(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao atualizar favoritos:', err);
    } finally {
      setRefreshing(false);
    }
  }, []);

  function getColors(index: number) {
    return {
      bgColor: COLORS_BG[index % COLORS_BG.length],
      tagColor: COLORS_TAG[index % COLORS_TAG.length],
      tagBg: COLORS_BG[index % COLORS_BG.length],
    };
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />

      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity style={styles.backBtn} onPress={() => router.back()}>
          <MaterialCommunityIcons name="arrow-left" size={22} color="#1B1630" />
        </TouchableOpacity>
        <View style={styles.headerInfo}>
          <Text style={styles.headerTitle}>Favoritos</Text>
          <Text style={styles.headerSubtitle}>{favorites.length} cursos</Text>
        </View>
      </View>

      {loading ? (
        <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
          <ActivityIndicator size="large" color="#5B18E6" />
        </View>
      ) : (
        <ScrollView
          contentContainerStyle={styles.listContainer}
          showsVerticalScrollIndicator={false}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#5B18E6" />}
        >
          {favorites.map((course, idx) => {
            const colors = getColors(idx);
            return (
              <TouchableOpacity
                key={course.id}
                style={styles.card}
                activeOpacity={0.7}
                onPress={() => router.push(`/curso/${course.id || course.curso_id}` as any)}
              >
                {/* Image placeholder */}
                <View style={[styles.imageBox, { backgroundColor: colors.bgColor }]}>
                  <MaterialCommunityIcons name="school" size={26} color={colors.tagColor} />
                </View>

                {/* Info */}
                <View style={styles.infoSection}>
                  <View style={styles.badgeRow}>
                    <View style={[styles.badge, { backgroundColor: colors.tagBg }]}>
                      <Text style={[styles.badgeText, { color: colors.tagColor }]}>
                        {course.categoria || course.category || 'Curso'}
                      </Text>
                    </View>
                    <TouchableOpacity>
                      <MaterialCommunityIcons name="heart" size={18} color="#E8433D" />
                    </TouchableOpacity>
                  </View>

                  <Text style={styles.courseTitle} numberOfLines={2}>
                    {course.nome || course.title || course.titulo}
                  </Text>
                  <Text style={styles.institutionText}>
                    {course.instituicao || course.institution || course.centro_nome || ''}
                  </Text>

                  <View style={styles.cardFooter}>
                    <View>
                      <Text style={styles.priceText}>
                        {course.preco === 0 || course.preco === '0' || course.preco === 'Gratuito'
                          ? 'Gratuito'
                          : `${course.preco || course.price || '0'} Kz`}
                      </Text>
                      {course.subsidio && (
                        <Text style={styles.subtitleText}>{course.subsidio}</Text>
                      )}
                    </View>
                    <TouchableOpacity style={styles.enrollBtn}>
                      <Text style={styles.enrollText}>Inscrever</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              </TouchableOpacity>
            );
          })}
        </ScrollView>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F6F5FA',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 14,
    gap: 14,
  },
  backBtn: {
    width: 42,
    height: 42,
    borderRadius: 13,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerInfo: {
    flex: 1,
  },
  headerTitle: {
    fontFamily: 'System',
    fontSize: 19,
    fontWeight: '800',
    color: '#1B1630',
  },
  headerSubtitle: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: '#8B8598',
    marginTop: 2,
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 20,
    gap: 14,
  },
  card: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    padding: 12,
    gap: 14,
  },
  imageBox: {
    width: 82,
    height: 82,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  infoSection: {
    flex: 1,
  },
  badgeRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 6,
  },
  badge: {
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 6,
  },
  badgeText: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '700',
  },
  courseTitle: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '800',
    color: '#1B1630',
    lineHeight: 18,
    marginBottom: 4,
  },
  institutionText: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#8B8598',
    marginBottom: 10,
  },
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  priceText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '800',
    color: '#1B1630',
  },
  subtitleText: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '600',
    color: '#159B5E',
    marginTop: 2,
  },
  enrollBtn: {
    backgroundColor: '#5B18E6',
    paddingHorizontal: 16,
    paddingVertical: 9,
    borderRadius: 10,
  },
  enrollText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#ffffff',
  },
});
