import React, { useState, useEffect, useCallback } from 'react';
import { StyleSheet, Text, View, ScrollView, TextInput, TouchableOpacity, RefreshControl, ActivityIndicator } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialCommunityIcons } from '@expo/vector-icons';
import { StatusBar } from 'expo-status-bar';
import { useRouter } from 'expo-router';
import { centros } from '@/services/api';

const COLORS_BG = ['#EDE7FE', '#DDF3E8', '#FBF0D9'];
const COLORS_TEXT = ['#5B18E6', '#159B5E', '#B57A12'];

export default function SchoolsScreen() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState('Todas');
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [schools, setSchools] = useState<any[]>([]);

  const filters = ['Todas', 'Luanda', 'Benguela', 'Huíla'];

  useEffect(() => {
    loadSchools();
  }, []);

  async function loadSchools() {
    try {
      setLoading(true);
      const data = await centros.list({ search: undefined });
      setSchools(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao carregar centros:', err);
    } finally {
      setLoading(false);
    }
  }

  const onRefresh = useCallback(async () => {
    try {
      setRefreshing(true);
      const data = await centros.list({ search: search || undefined });
      setSchools(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro ao atualizar centros:', err);
    } finally {
      setRefreshing(false);
    }
  }, [search]);

  async function handleSearch(text: string) {
    setSearch(text);
    try {
      const data = await centros.list({ search: text || undefined });
      setSchools(Array.isArray(data) ? data : data?.results || []);
    } catch (err) {
      console.error('Erro na pesquisa:', err);
    }
  }

  async function handleFollow(id: number | string) {
    try {
      await centros.seguir(id);
      setSchools((prev) =>
        prev.map((s) =>
          (s.id === id ? { ...s, seguindo: !s.seguindo, following: !s.following } : s)
        )
      );
    } catch (err) {
      console.error('Erro ao seguir centro:', err);
    }
  }

  const filteredSchools = schools.filter((school) => {
    const matchesFilter = activeFilter === 'Todas' || school.localizacao === activeFilter || school.location === activeFilter;
    return matchesFilter;
  });

  function getColors(index: number) {
    return {
      bgColor: COLORS_BG[index % COLORS_BG.length],
      textColor: COLORS_TEXT[index % COLORS_TEXT.length],
    };
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="dark" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Instituições</Text>
      </View>

      {/* Search bar */}
      <View style={styles.searchContainer}>
        <View style={styles.searchBox}>
          <MaterialCommunityIcons name="magnify" size={20} color="#9A93AD" />
          <TextInput
            style={styles.searchInput}
            placeholder="Procurar escolas…"
            placeholderTextColor="#9A93AD"
            value={search}
            onChangeText={handleSearch}
          />
        </View>
      </View>

      {/* Filter pills */}
      <View style={styles.filterRow}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.filterContainer}>
          {filters.map((filter) => (
            <TouchableOpacity
              key={filter}
              style={[styles.filterPill, activeFilter === filter && styles.filterPillActive]}
              onPress={() => setActiveFilter(filter)}
            >
              <Text style={[styles.filterText, activeFilter === filter && styles.filterTextActive]}>
                {filter}
              </Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
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
          {filteredSchools.map((school, idx) => {
            const colors = getColors(idx);
            const abbr = school.sigla || school.abbr || (school.nome || school.name || '').substring(0, 2).toUpperCase();
            const isFollowing = school.seguindo || school.following;
            const courseCount = school.total_cursos || school.cursos || school.courses || 0;

            return (
              <TouchableOpacity
                key={school.id}
                style={styles.schoolCard}
                activeOpacity={0.7}
                onPress={() => router.push(`/escola/${school.id}` as any)}
              >
                {/* Avatar */}
                <View style={[styles.avatar, { backgroundColor: colors.bgColor }]}>
                  <Text style={[styles.avatarText, { color: colors.textColor }]}>{abbr}</Text>
                </View>

                {/* Info */}
                <View style={styles.infoSection}>
                  <View style={styles.nameRow}>
                    <Text style={styles.schoolName} numberOfLines={1}>
                      {school.nome || school.name}
                    </Text>
                    {(school.verificado || school.verified) && (
                      <MaterialCommunityIcons name="check-decagram" size={15} color="#5B18E6" />
                    )}
                  </View>
                  <View style={styles.locationRow}>
                    <MaterialCommunityIcons name="map-marker-outline" size={13} color="#8B8598" />
                    <Text style={styles.locationText}>
                      {school.localizacao || school.location || ''}
                    </Text>
                    <Text style={styles.courseCount}>· {courseCount} cursos</Text>
                  </View>
                </View>

                {/* Follow button */}
                <TouchableOpacity
                  style={[styles.followBtn, isFollowing && styles.followBtnActive]}
                  onPress={() => handleFollow(school.id)}
                >
                  <Text style={[styles.followText, isFollowing && styles.followTextActive]}>
                    {isFollowing ? 'A seguir' : 'Seguir'}
                  </Text>
                </TouchableOpacity>
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
    paddingHorizontal: 20,
    paddingVertical: 14,
  },
  headerTitle: {
    fontFamily: 'System',
    fontSize: 19,
    fontWeight: '800',
    color: '#1B1630',
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
    paddingVertical: 12,
    gap: 10,
  },
  searchInput: {
    flex: 1,
    fontFamily: 'System',
    fontSize: 14,
    color: '#1B1630',
    padding: 0,
  },
  filterRow: {
    marginBottom: 6,
  },
  filterContainer: {
    paddingHorizontal: 20,
    gap: 9,
  },
  filterPill: {
    paddingHorizontal: 16,
    paddingVertical: 9,
    borderRadius: 99,
    backgroundColor: '#ffffff',
    borderWidth: 1,
    borderColor: '#ECE8F3',
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
  listContainer: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 20,
    gap: 14,
  },
  schoolCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#ffffff',
    borderRadius: 18,
    borderWidth: 1,
    borderColor: '#ECE8F3',
    padding: 14,
    gap: 14,
  },
  avatar: {
    width: 52,
    height: 52,
    borderRadius: 14,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    fontFamily: 'System',
    fontSize: 18,
    fontWeight: '800',
  },
  infoSection: {
    flex: 1,
  },
  nameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  schoolName: {
    fontFamily: 'System',
    fontSize: 14,
    fontWeight: '700',
    color: '#1B1630',
    flexShrink: 1,
  },
  locationRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 4,
  },
  locationText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: '#8B8598',
  },
  courseCount: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '500',
    color: '#8B8598',
  },
  followBtn: {
    paddingHorizontal: 16,
    paddingVertical: 9,
    borderRadius: 10,
    borderWidth: 1.5,
    borderColor: '#5B18E6',
  },
  followBtnActive: {
    backgroundColor: '#5B18E6',
    borderColor: '#5B18E6',
  },
  followText: {
    fontFamily: 'System',
    fontSize: 12,
    fontWeight: '700',
    color: '#5B18E6',
  },
  followTextActive: {
    color: '#ffffff',
  },
});
