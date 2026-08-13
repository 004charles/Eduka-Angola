import React, { useState, useEffect, useCallback, useRef } from 'react';
import { StyleSheet, Text, View, ScrollView, TextInput, TouchableOpacity, ActivityIndicator, RefreshControl } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { cursos, categorias } from '@/services/api';

export default function CursosScreen() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState<number | null>(null);
  const [courseList, setCourseList] = useState<any[]>([]);
  const [categoryList, setCategoryList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const filters = ['Categoria', 'Duração', 'Preço', 'Com bolsa'];

  const fetchData = useCallback(async (searchTerm?: string, categoriaId?: number | null) => {
    try {
      const [coursesData, catsData] = await Promise.all([
        cursos.list({ search: searchTerm || undefined, categoria: categoriaId ?? undefined }),
        categorias.list(),
      ]);
      const list = Array.isArray(coursesData) ? coursesData : (coursesData as any).results ?? [];
      setCourseList(list);
      const cats = Array.isArray(catsData) ? catsData : (catsData as any).results ?? [];
      setCategoryList(cats);
    } catch (err) {
      console.error('Failed to load courses:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchData(search || undefined, activeFilter);
  }, [fetchData, search, activeFilter]);

  const handleSearch = useCallback(
    (text: string) => {
      setSearch(text);
      if (debounceRef.current) clearTimeout(debounceRef.current);
      debounceRef.current = setTimeout(() => {
        fetchData(text || undefined, activeFilter);
      }, 400);
    },
    [fetchData, activeFilter],
  );

  const handleFilterPress = useCallback(
    (filterLabel: string, index: number) => {
      const categoryId = categoryList[index]?.id ?? null;
      setActiveFilter(categoryId);
      fetchData(search || undefined, categoryId);
    },
    [categoryList, fetchData, search],
  );

  const badgeColors = [
    { bg: '#EDE7FE', text: '#5B18E6' },
    { bg: '#DDF3E8', text: '#159B5E' },
    { bg: '#FBF0D9', text: '#B57A12' },
    { bg: '#FDE7E7', text: '#E8433D' },
    { bg: '#E7F0FD', text: '#3B7DD8' },
  ];

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Explorar cursos</Text>
        <View style={styles.headerActions}>
          <TouchableOpacity
            style={styles.institutionBtn}
            onPress={() => router.push('/escolas')}
          >
            <MaterialCommunityIcons name="domain" size={18} color="#5B18E6" />
            <Text style={styles.institutionBtnText}>Instituições</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerFilterBtn}>
            <MaterialCommunityIcons name="tune-vertical" size={20} color="#5B18E6" />
          </TouchableOpacity>
        </View>
      </View>

      {/* Search */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <MaterialCommunityIcons name="magnify" size={20} color="#9A93AD" />
          <TextInput
            style={styles.searchInput}
            placeholder="Contabilidade…"
            placeholderTextColor="#9A93AD"
            value={search}
            onChangeText={handleSearch}
          />
        </View>
      </View>

      {/* Filter pills */}
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        contentContainerStyle={styles.filterContainer}
      >
        {filters.map((f, i) => {
          const isActive = activeFilter === (categoryList[i]?.id ?? null);
          return (
            <TouchableOpacity
              key={f}
              style={[styles.filterPill, isActive && styles.filterPillActive]}
              onPress={() => handleFilterPress(f, i)}
            >
              <Text style={[styles.filterText, isActive && styles.filterTextActive]}>
                {f}
              </Text>
            </TouchableOpacity>
          );
        })}
      </ScrollView>

      {/* Count */}
      <Text style={styles.countText}>{courseList.length} cursos encontrados</Text>

      {/* Course list */}
      <ScrollView
        contentContainerStyle={styles.listContainer}
        showsVerticalScrollIndicator={false}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#5B18E6" />}
      >
        {loading ? (
          <ActivityIndicator size="large" color="#5B18E6" style={{ marginTop: 40 }} />
        ) : courseList.length > 0 ? (
          courseList.map((course, index) => {
            const color = badgeColors[index % badgeColors.length];
            return (
              <TouchableOpacity
                key={course.id}
                style={styles.card}
                activeOpacity={0.7}
                onPress={() => router.push(`/curso/${course.id}`)}
              >
                <View style={[styles.cardImage, { backgroundColor: color.bg }]}>
                  <MaterialCommunityIcons name="school" size={28} color={color.text} />
                </View>
                <View style={styles.cardBody}>
                  <View style={[styles.badge, { backgroundColor: color.bg }]}>
                    <Text style={[styles.badgeText, { color: color.text }]}>{course.categoria_nome ?? 'Curso'}</Text>
                  </View>
                  <Text style={styles.cardTitle} numberOfLines={1}>{course.titulo ?? course.title}</Text>
                  <Text style={styles.cardInstitution}>{course.centro_nome ?? course.institution ?? ''}</Text>
                  <View style={styles.cardMeta}>
                    <View style={styles.metaItem}>
                      <MaterialCommunityIcons name="star" size={13} color="#F5A623" />
                      <Text style={styles.metaText}>{course.rating ?? '4.8'}</Text>
                    </View>
                    <View style={styles.metaItem}>
                      <MaterialCommunityIcons name="clock-outline" size={13} color="#8B8598" />
                      <Text style={styles.metaText}>{course.duracao ?? course.duration ?? ''}</Text>
                    </View>
                  </View>
                </View>
                <View style={styles.cardPriceCol}>
                  <Text style={styles.priceText}>{course.preco != null ? `${Number(course.preco).toLocaleString('pt-AO')} Kz` : course.price ?? 'Gratuito'}</Text>
                  <TouchableOpacity style={styles.arrowBtn}>
                    <MaterialCommunityIcons name="arrow-right" size={16} color="#5B18E6" />
                  </TouchableOpacity>
                </View>
              </TouchableOpacity>
            );
          })
        ) : (
          <Text style={{ color: '#8B8598', textAlign: 'center', marginTop: 40 }}>Nenhum curso encontrado</Text>
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
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 14,
  },
  headerTitle: {
    fontFamily: 'System',
    fontSize: 19,
    fontWeight: '800',
    color: '#1B1630',
  },
  headerFilterBtn: {
    width: 42,
    height: 42,
    borderRadius: 13,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerActions: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  institutionBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 14,
    height: 42,
    borderRadius: 13,
    backgroundColor: '#EDE7FE',
    borderWidth: 1,
    borderColor: '#D4C4FE',
  },
  institutionBtnText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5B18E6',
  },
  searchContainer: {
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  searchBox: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    borderRadius: 16,
    paddingHorizontal: 16,
    paddingVertical: 11,
    gap: 10,
  },
  searchInput: {
    flex: 1,
    fontFamily: 'System',
    fontSize: 14,
    color: '#1B1630',
    padding: 0,
  },
  filterContainer: {
    paddingHorizontal: 20,
    gap: 9,
    paddingBottom: 8,
  },
  filterPill: {
    paddingHorizontal: 15,
    paddingVertical: 9,
    borderRadius: 99,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
    height: 38,
    justifyContent: 'center',
  },
  filterPillActive: {
    backgroundColor: '#5B18E6',
    borderColor: '#5B18E6',
  },
  filterText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5A5567',
  },
  filterTextActive: {
    color: '#ffffff',
  },
  countText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '600',
    color: '#8B8598',
    paddingHorizontal: 20,
    marginBottom: 10,
  },
  listContainer: {
    paddingHorizontal: 20,
    paddingBottom: 30,
    gap: 14,
  },
  card: {
    flexDirection: 'row',
    backgroundColor: '#ffffff',
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    padding: 12,
    gap: 14,
  },
  cardImage: {
    width: 86,
    height: 86,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center',
  },
  cardBody: {
    flex: 1,
  },
  badge: {
    alignSelf: 'flex-start',
    paddingHorizontal: 7,
    paddingVertical: 3,
    borderRadius: 6,
    marginBottom: 5,
  },
  badgeText: {
    fontFamily: 'System',
    fontSize: 10,
    fontWeight: '700',
  },
  cardTitle: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '800',
    color: '#1B1630',
    lineHeight: 18,
    marginBottom: 3,
  },
  cardInstitution: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '500',
    color: '#8B8598',
    marginBottom: 6,
  },
  cardMeta: {
    flexDirection: 'row',
    gap: 12,
  },
  metaItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  metaText: {
    fontFamily: 'System',
    fontSize: 11,
    fontWeight: '600',
    color: '#8B8598',
  },
  cardPriceCol: {
    alignItems: 'flex-end',
    justifyContent: 'space-between',
  },
  priceText: {
    fontFamily: 'System',
    fontSize: 13,
    fontWeight: '800',
    color: '#1B1630',
  },
  arrowBtn: {
    width: 28,
    height: 28,
    borderRadius: 8,
    backgroundColor: '#EDE7FE',
    alignItems: 'center',
    justifyContent: 'center',
  },
});
